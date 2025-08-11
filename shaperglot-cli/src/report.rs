use clap::Args;
use shaperglot::Checker;
use std::{
    collections::{HashMap, HashSet},
    path::PathBuf,
};

use crate::show_fixes;

#[derive(Args)]
pub struct ReportArgs {
    /// Number of fixes left to be considered nearly supported
    #[arg(long, default_value_t = 5, hide = true)]
    nearly: usize,
    /// Verbosity
    #[arg(short, long, action = clap::ArgAction::Count, hide = true)]
    verbose: u8,
    /// Output check results as JSON
    #[arg(long, hide = true)]
    json: bool,
    /// Output check results as CSV
    #[arg(long, hide = true)]
    csv: bool,
    /// Regular expression to filter languages
    #[arg(long)]
    filter: Option<String>,
    /// Output a fix summary
    #[arg(long, hide = true)]
    fix: bool,
    /// Font file to check
    font: PathBuf,
}

pub fn report_command(args: &ReportArgs, language_database: shaperglot::Languages) {
    let font_binary = std::fs::read(args.font.as_path())
        .map_err(|e| {
            eprintln!("Failed to read font file {}: {}", args.font.display(), e);
            std::process::exit(1);
        })
        .unwrap();
    let checker = Checker::new(&font_binary).expect("Failed to load font");
    let mut fixes_required = HashMap::new();
    let mut has_failed = false;
    for language in language_database.iter() {
        if let Some(filter) = &args.filter {
            if !language.id().contains(filter) {
                continue;
            }
        }
        let results = checker.check(language);
        if results.is_unknown() {
            continue;
        }
        has_failed |= !results.is_nearly_success(args.nearly);
        if results.fixes_required() > 0 && results.fixes_required() <= args.nearly {
            println!(
                "Font nearly supports {} ({}): {:.0}% ({} fixes required)",
                language.id(),
                language.name(),
                results.score(),
                results.fixes_required()
            );
        } else {
            println!("{}", results.to_summary_string(language));
        }
        if args.fix {
            for (category, fixes) in results.unique_fixes() {
                fixes_required
                    .entry(category)
                    .or_insert_with(HashSet::new)
                    .extend(fixes);
            }
        }
    }
    if args.fix {
        show_fixes(&fixes_required);
    }
    if has_failed {
        std::process::exit(1);
    }
}
