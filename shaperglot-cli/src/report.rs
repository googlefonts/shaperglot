use clap::Args;
use shaperglot::Checker;
use std::path::PathBuf;

#[derive(Args)]
pub struct ReportArgs {
    /// Number of fixes left to be considered nearly supported
    #[arg(long, default_value_t = 5)]
    nearly: usize,
    /// Verbosity
    #[arg(short, long, action = clap::ArgAction::Count)]
    verbose: u8,
    /// Output check results as JSON
    #[arg(long)]
    json: bool,
    /// Output check results as CSV
    #[arg(long)]
    csv: bool,
    /// Regular expression to filter languages
    #[arg(long)]
    filter: Option<String>,
    /// Output a fix summary
    #[arg(long)]
    fix: bool,
    /// Font file to check
    font: PathBuf,
}

pub fn report_command(args: &ReportArgs, language_database: shaperglot::Languages) {
    let font_binary = std::fs::read(args.font.as_path()).expect("Failed to read font file");
    let checker = Checker::new(&font_binary).expect("Failed to load font");
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
        println!("{}", results.to_summary_string(args.nearly, language));
    }
}
