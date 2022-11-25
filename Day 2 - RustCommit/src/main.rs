use git::Repository;
use std::{env, path::PathBuf};

fn main() {
    let dir: PathBuf = env::current_dir().unwrap();

    let repo = match Repository::open(dir) {
        Ok(repo) => repo,
        Err(e) => panic!("failed to open: {}", e),
    };
}