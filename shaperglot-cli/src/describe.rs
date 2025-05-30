use clap::Args;

#[derive(Args)]
pub struct DescribeArgs {
    /// Output check definition as TOML
    #[arg(long)]
    json: bool,
    /// Language name or ID to describe
    language: String,
}

pub fn describe_command(args: &DescribeArgs, language_database: shaperglot::Languages) {
    if let Some(language) = language_database.get_language(&args.language) {
        if args.json {
            let json = serde_json::to_string_pretty(&language.checks).unwrap();
            println!("{}", json);
            // }
        } else {
            for check in language.checks.iter() {
                println!("{}", check.description);
            }
        }
    } else {
        println!("Language not found ({})", &args.language);
    }
}
