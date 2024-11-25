use check::{check_command, CheckArgs};
use clap::{Parser, Subcommand};
use report::{report_command, ReportArgs};

mod check;
mod report;

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
#[command(propagate_version = true)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Check language support
    Check(CheckArgs),
    /// Report language support
    Report(ReportArgs),
}

fn main() {
    let cli = Cli::parse();
    let language_database = shaperglot::Languages::new();

    match &cli.command {
        Commands::Check(args) => {
            check_command(args, language_database);
        }
        Commands::Report(args) => {
            report_command(args, language_database);
        }
    }
}
