use clap::Args;
use shaperglot::Checker;
use std::path::PathBuf;

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
        println!("{}", results.to_summary_string(language));
    }
}
