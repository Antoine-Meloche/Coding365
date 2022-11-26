use git::Repository;
use std::{env, path::{PathBuf, Path}, process};

extern crate termion;
use termion::{color};

fn main() {
    let args: Vec<String> = env::args().collect();
    let dir: PathBuf;
    let mut path: &String = &String::from("");
    
    if args.contains(&String::from("-p")) {
        let index: usize = &args.iter().position(|x| x == "-p").unwrap() + 1;
        
        if args.len() <= index {
            println!("{}ERR: No folder was set whilst using the '-p' flag. [refer to --help for more info]{}", color::Fg(color::Red), color::Fg(color::White));
            process::exit(1);
        }
        path = &args[index];

        if Path::new(path).exists() {
            dir = PathBuf::from(path);
        } else {
            println!("{}ERR: provided path '{}' does not exist.{}", color::Fg(color::Red), path, color::Fg(color::White));
            process::exit(2);
        }
    } else {
        dir = env::current_dir().unwrap();
    }


    let _repo: Repository = match Repository::open(dir) {
        Ok(repo) => repo,
        Err(_e) => {
            if path.is_empty() {
                println!("{}ERR: No git repository exists in current working directory.{}", color::Fg(color::Red), color::Fg(color::White));
            } else {
                println!("{}ERR: No Git repository exists at '{}'.{}", color::Fg(color::Red), path, color::Fg(color::White));
            }
            process::exit(2);
        },
    };
}