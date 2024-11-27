use check::{check_command, CheckArgs};
use clap::{Parser, Subcommand};
use describe::{describe_command, DescribeArgs};
use report::{report_command, ReportArgs};

mod check;
mod describe;
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
    /// Describe what is needed to support a language
    Describe(DescribeArgs),
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
        Commands::Describe(args) => {
            describe_command(args, language_database);
        }
    }
}
