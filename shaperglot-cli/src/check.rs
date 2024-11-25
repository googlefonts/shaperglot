use clap::Args;
use itertools::Itertools;
use shaperglot::{Checker, Reporter};
use std::{
    collections::{HashMap, HashSet},
    path::PathBuf,
};

#[derive(Args)]
pub struct CheckArgs {
    /// Number of fixes left to be considered nearly supported
    #[arg(long, default_value_t = 5)]
    nearly: usize,
    /// Verbosity
    #[arg(short, long, action = clap::ArgAction::Count)]
    verbose: u8,
    /// Output check results as JSON
    #[arg(long)]
    json: bool,
    /// Output a fix summary
    #[arg(long)]
    fix: bool,
    /// Font file to check
    font: PathBuf,
    /// Language to check
    languages: Vec<String>,
}

pub fn check_command(args: &CheckArgs, language_database: shaperglot::Languages) {
    let font_binary = std::fs::read(args.font.as_path()).expect("Failed to read font file");
    let checker = Checker::new(&font_binary).expect("Failed to load font");
    let mut fixes_required = HashMap::new();
    for language in args.languages.iter() {
        if let Some(language) = language_database.get_language(language) {
            let results = checker.check(language, false);
            if args.json {
                println!("{}", serde_json::to_string(&results).unwrap());
                continue;
            }
            let score = if results.is_unknown() {
                ""
            } else {
                &format!(": {:.0}%", results.score())
            };
            let status = if results.is_unknown() {
                "Cannot determine whether font supports "
            } else if results.is_nearly_success(args.nearly) {
                "Font nearly supports "
            } else if results.is_success() {
                "Font supports "
            } else {
                "Font does not fully support "
            };
            eprintln!(
                "{}language {} ({}){}",
                status,
                language.id(),
                language.name(),
                score
            );
            show_result(&results, args.verbose);
            if args.fix {
                for (category, fixes) in results.unique_fixes() {
                    fixes_required
                        .entry(category)
                        .or_insert_with(HashSet::new)
                        .extend(fixes);
                }
            }
        } else {
            eprintln!("Language not found");
        }
    }
    if args.fix {
        show_fixes(&fixes_required);
    }
}

fn show_result(results: &Reporter, verbose: u8) {
    for check in results.iter() {
        if verbose == 0 && check.problems.is_empty() {
            continue;
        }
        eprintln!("   {}: {}", check.status, check.summary_result());
        if verbose > 1 {
            eprintln!("  {}", check.check_description);
        }
        if verbose > 1 || (verbose == 1 && !check.problems.is_empty()) {
            for problem in check.problems.iter() {
                eprintln!("  * {}", problem.message);
            }
        }
    }
    println!();
}

fn show_fixes(fixes: &HashMap<String, HashSet<String>>) {
    if fixes.is_empty() {
        return;
    }
    eprintln!("\nTo add full support:");
    for (category, fixes) in fixes {
        eprintln!(
            "* {}:",
            match category.as_str() {
                "add_anchor" => "Add anchors between the following glyphs",
                "add_codepoint" => "Add the following codepoints to the font",
                "add_feature" => "Add the following features to the font",
                _ => category,
            }
        );
        eprintln!("    {}", fixes.iter().join(", "));
    }
}
