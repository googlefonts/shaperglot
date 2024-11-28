const shaperglotWorker = new Worker(new URL("./webworker.js", import.meta.url));
const fix_descriptions = {
  add_anchor: "Add anchors between the following glyphs",
  add_codepoint: "Add the following codepoints to the font",
  add_feature: "Add the following features to the font",
};
const STATUS_INT = {
  "Complete": 5,
  "Supported": 4,
  "Incomplete": 3,
  "Unsupported": 2,
  "None": 1,
  "Indeterminate": 0,
};

function commify(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

jQuery.fn.shake = function (interval, distance, times) {
  interval = typeof interval == "undefined" ? 100 : interval;
  distance = typeof distance == "undefined" ? 10 : distance;
  times = typeof times == "undefined" ? 3 : times;
  var jTarget = $(this);
  jTarget.css("position", "relative");
  for (var iter = 0; iter < times + 1; iter++) {
    jTarget.animate(
      {
        left: iter % 2 == 0 ? distance : distance * -1,
      },
      interval
    );
  }
  return jTarget.animate(
    {
      left: 0,
    },
    interval
  );
};

class Shaperglot {
  constructor() {
    this.font = null;
    this.scripts = null;
    this.regions = null;
  }

  dropFile(files, element) {
    if (!files[0].name.match(/\.[ot]tf$/i)) {
      $(element).shake();
      return;
    }
    window.thing = files[0];
    $("#filename").text(files[0].name);
    let style = document.styleSheets[0].cssRules[0].style;
    style.setProperty("src", "url(" + URL.createObjectURL(files[0]) + ")");
    var reader = new FileReader();
    let that = this;
    reader.onload = function (e) {
      let u8 = new Uint8Array(this.result);
      that.font = u8;
      that.letsDoThis();
    };
    reader.readAsArrayBuffer(files[0]);
  }

  progress_callback(message) {
    // console.log("Got message", message);
    if ("ready" in message) {
      $("#bigLoadingModal").hide();
      $("#startModal").show();
      this.scripts = message.scripts;
      this.regions = message.regions;
    } else if ("results" in message) {
      $("#spinnerModal").hide();
      if (message.family_name) {
        $("#filename").text(message.family_name);
      }
      this.renderResults(message.results);
    }
  }

  renderResults(results) {
    let ix = 0;
    let issues_by_script = {};
    let count_supported_by_script = {};
    for (let [language, result, problems] of results) {
      issues_by_script[language.script] =
        issues_by_script[language.script] || [];
      issues_by_script[language.script].push([language, result, problems]);
      if (result === "Supported" || result === "Complete" || result === "Incomplete") {
        count_supported_by_script[language.script] =
          (count_supported_by_script[language.script] || 0) + 1;
      }
    }

    for (let [script, languages] of Object.entries(issues_by_script).sort(
      ([script_a, _languages_a], [script_b, _languages_b]) =>
        (count_supported_by_script[script_b] || 0) -
        (count_supported_by_script[script_a] || 0)
    )) {
      let supported = count_supported_by_script[script] || 0;
      let card = $(`
      <div class="card script-${supported}">
<div class="card-header" id="script${ix}" class="p-0">
  <h5 class="mb-0 text-center">
    <a class="collapsed p-0" type="button" data-toggle="collapse" data-target="#collapse${ix}" aria-expanded="true" aria-controls="collapse${ix}">
      ${this.scripts[script].name}<br>
      <small>(${supported} supported languages)</small>
    </a>
  </h5>
</div>

<div id="collapse${ix}" class="collapse" aria-labelledby="script${ix}" data-parent="#scriptlist">
  <div class="card-body">
   
  </div>
</div>
</div>
`);
      ix += 1;
      let pilldiv = $("<div></div>");
      pilldiv.addClass("nav nav-pills");
      card.find(".card-body").append(pilldiv);
      for (let language of languages) {
        let problemSet = language[2];
        let total_weight = problemSet
          .map((r) => r.weight)
          .reduce((a, b) => a + b);
        let weighted_scores = problemSet.map((r) => r.score * r.weight);
        let total_score = weighted_scores.reduce((a, b) => a + b);
        problemSet.score = (total_score / total_weight) * 100.0;
      }

      for (let [language, result, problems] of languages.sort(
        (a, b) => STATUS_INT[a[1]] - STATUS_INT[b[1]] || a[0].name.localeCompare(b[0].name)
      )) {
        var thispill = $(`
        <button
          class="nav-link status-${result}"
          type="button"
          role="tab"
          >${language.name}</button>
      `);
        thispill.data("languagedata", language);
        thispill.data("problemset", problems);
        thispill.data("result", result);
        pilldiv.append(thispill);
        thispill.on("click", (el) => {
          this.renderProblemSet($(el.target));
          $(el.target).siblings().removeClass("active");
          $(el.target).addClass("active");
        });
      }
      $("#scriptlist").append(card);
    }
  }

  renderProblemSet(el) {
    let filename = $("#filename").text();
    let result = $("#language-content div");
    result.empty();
    var problemSet = el.data("problemset");
    let language = el.data("languagedata");
    let langname = language.preferred_name || language.name;
    result.append(`<h1>${langname} (${Math.round(problemSet.score)}%)</h1>`);
    if (language.autonym) {
      result.append(`<h2>(${language.autonym})</h2>`);
    }
    result.append(
      `<p class="mb-0"><b>ISO369-3 Code</b>: <code>${language.id}</code></p>`
    );
    if (language.population) {
      result.append(
        `<p class="mb-0"><b>Population</b>: ${commify(language.population)}</p>`
      );
    }
    if (language.region) {
      let regions_list = language.region
        .map((r) => this.regions[r].name)
        .join(", ");
      result.append(`<p class="mb-0"><b>Regions</b>: ${regions_list}</p>`);
    }
    let status = el.data("result");

    if (language.sample_text) {
      let extra_class = "";
      if (status == "Complete" || status == "Supported" || status == "Incomplete") {
        extra_class = "testfont";
      }
      result.append($(
        `<p class="mb-0"><b>Sample text</b>:<blockquote class="blockquote ${extra_class}">${language.sample_text.specimen_32} ${language.sample_text.specimen_21}</blockquote></p>`
      ));
    }


    if (status == "Complete") {
      result.append(
        `<div class="p-3 mb-2 alert alert-success">${filename} comprehensively supports ${langname}!</div>`
      );
    } else if (status == "Supported") {
        result.append(
          `<div class="p-3 mb-2 alert alert-success">${filename} supports ${langname} well (but further support is possible).</div>`
        );
  
    } else if (status == "Incomplete") {
      result.append(
        `<div class="p-3 mb-2 alert alert-success">${filename} supports ${langname}.</div>`
      );
    } else if (status == "Unsupported") {
      result.append(
        `<div class="p-3 mb-2 alert alert-danger">${filename} does not support ${langname}.</div>`
      );
    } else if (status == "None") {
      result.append(
        `<div class="p-3 mb-2 alert alert-dark">${filename} does not attempt to support ${langname}.</div>`
      );
    } else {
      result.append(
        `<div class="p-3 mb-2 alert alert-dark">Cannot determine whether ${filename} supports ${langname}.</div>`
      );
    }
    // result.append(`<pre>${JSON.stringify(problemSet)}</pre>`);

    let problem_html = $("<dl></dl>");
    let fixdiv = $(`<div><b>For full support:</b></div>`);
    let fixes_needed = {};
    for (var check of problemSet) {
      let {
        check_name,
        check_description,
        score,
        weight,
        problems,
        total_checks,
        status,
        fixes,
      } = check;
      let mark = status == "Pass" ? "✅" : "❌";

      problem_html.append(
        `<dt>
        <details>
          <summary>${check_name} ${mark} (${Math.round(
            score * weight * 100
          ) / 100}/${weight} points)
          </summary>
          <blockquote class="bg-light">${check_description}
          </blockquote>
        </dt>`
      );
      let dd = $(`<dd>
       
        </dd>`);
      problem_html.append(dd);
      if (problems.length > 0) {
        dd.append(`<p><b>Problems:</b><ul></ul></p>`);
      } else {
        problem_html.find("details").last().append(`<ul><li>No problems found!</li></ul>`);
      }
      for (var problem of problems) {
        let { check_name, message, fixes } = problem;
        dd.find("ul").append(`<li>${message}</li>`);

        for (var fix of fixes || []) {
          let { fix_type, fix_thing } = fix;
          fixes_needed[fix_type] = fixes_needed[fix_type] || [];
          fixes_needed[fix_type].push(fix_thing);
        }
      }
    }

    for (var [fix_type, fix_things] of Object.entries(fixes_needed)) {
      let fix_thing = fix_things.join(", ");
      fixdiv.append(`<li>${fix_descriptions[fix_type]}: ${fix_thing}</li>`);
    }

    if ($(fixdiv).children().length > 1) {
      problem_html.append($("<hr>"));
      problem_html.append(fixdiv);
    }

    result.append(problem_html);
    // result.append(`<pre>${JSON.stringify(language)}</pre>`);
  }

  letsDoThis() {
    $("#startModal").hide();
    $("#spinnerModal").show();
    shaperglotWorker.postMessage({
      font: this.font,
    });
  }
}

$(function () {
  window.shaperglot = new Shaperglot();
  shaperglotWorker.onmessage = (e) =>
    window.shaperglot.progress_callback(e.data);
  $("#bigLoadingModal").show();

  $(".fontdrop").on("dragover dragenter", function (e) {
    e.preventDefault();
    e.stopPropagation();
    $(this).addClass("dragging");
  });
  $(".fontdrop").on("dragleave dragend", function (e) {
    $(this).removeClass("dragging");
  });

  $(".fontdrop").on("drop", function (e) {
    console.log("Drop!");
    $(this).removeClass("dragging");
    if (
      e.originalEvent.dataTransfer &&
      e.originalEvent.dataTransfer.files.length
    ) {
      e.preventDefault();
      e.stopPropagation();
      window.shaperglot.dropFile(e.originalEvent.dataTransfer.files, this);
    }
  });
});
