use git::{
    string_array::StringArray, Commit, Config, Error, Oid, Reference, Remote, Repository,
    Signature, Tree, PushOptions,
};
use once_cell::sync::Lazy;
use std::{
    env, io,
    io::{Read, Write},
    path::{Path, PathBuf},
    process,
};

extern crate termion;
use termion::color;

static mut CONFIG: Lazy<Config> = Lazy::new(|| {
    git::Config::open_default()
        .ok()
        .expect("ERR: Failed to fetch git configuration.")
});

pub fn main() {
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
            println!(
                "{}ERR: provided path '{}' does not exist.{}",
                color::Fg(color::Red),
                path,
                color::Fg(color::White)
            );
            process::exit(2);
        }
    } else {
        dir = env::current_dir().unwrap();
    }

    let repo: Repository = match Repository::open(dir) {
        Ok(repo) => repo,
        Err(_e) => {
            if path.is_empty() {
                println!(
                    "{}ERR: No git repository exists in current working directory.{}",
                    color::Fg(color::Red),
                    color::Fg(color::White)
                );
            } else {
                println!(
                    "{}ERR: No Git repository exists at '{}'.{}",
                    color::Fg(color::Red),
                    path,
                    color::Fg(color::White)
                );
            }
            process::exit(2);
        }
    };

    stage_changes(&repo);
    commit(&repo);
    push(&repo);
}

fn stage_changes(repo: &Repository) {
    let mut index = repo.index().unwrap();
    index
        .add_all(&["."], git::IndexAddOption::DEFAULT, None)
        .unwrap();
    index.write().unwrap();
    println!(
        "{}  ➜ Changes staged{}",
        color::Fg(color::Green),
        color::Fg(color::White)
    );
}

fn commit(repo: &Repository) {
    let message: [String; 2] = commit_message();
    let title: &String = &message[0];
    let body: &String = &message[1];

    let verified: bool = commit_verify(title, body);
    if verified == false {
        println!(
            "\n{}  ✘ Commit aborted{}",
            color::Fg(color::Yellow),
            color::Fg(color::White)
        );
        process::exit(1);
    }

    let signature: Signature;
    unsafe {
        signature = Signature::now(
            &CONFIG.get_string("user.name").unwrap()[..],
            &CONFIG.get_string("user.email").unwrap()[..],
        )
        .unwrap();
    }
    let oid: Oid = repo.index().unwrap().write_tree().unwrap();
    let tree: Tree = repo.find_tree(oid).unwrap();

    let head_result: Result<Reference, Error> = repo.head();
    let has_head = match head_result {
        Ok(_head) => true,
        Err(_e) => false,
    };
    if has_head {
        let parent_commit_result: Result<Commit, Error> = repo.head().unwrap().peel_to_commit();
        let mut has_parent: bool = false;
        match parent_commit_result {
            Ok(_commit) => {
                has_parent = true;
            }
            Err(_e) => {}
        };

        if has_parent {
            let parent_commit = &[&repo.head().unwrap().peel_to_commit().unwrap()];
            repo.commit(
                Some("HEAD"),
                &signature,
                &signature,
                &format!("{}\n\n{}", title, body)[..],
                &tree,
                parent_commit,
            )
            .unwrap();
        } else {
            repo.commit(
                Some("HEAD"),
                &signature,
                &signature,
                &format!("{}\n\n{}", title, body)[..],
                &tree,
                &[],
            )
            .unwrap();
        }
    } else {
        repo.commit(
            Some("HEAD"),
            &signature,
            &signature,
            &format!("{}\n\n{}", title, body)[..],
            &tree,
            &[],
        )
        .unwrap();
    }

    println!(
        "{}  ➜ Committed{}",
        color::Fg(color::Green),
        color::Fg(color::White)
    );
}

fn commit_message() -> [String; 2] {
    println!(
        "
    [1] BUGFIX: fixed a bug
    [2] FEAT: added a feature
    [3] REFAC: code refactoring
    [4] DOCS: change to documentation only
    [5] STYLE: change to formatting only
    [6] TEST: change, addition to tests only
    [7] Custom"
    );

    print!("Which corresponds to the type of your commit [1-7]: ");
    io::stdout().flush().unwrap();
    let mut commit_type_choice: String = String::new();
    io::stdin()
        .read_line(&mut commit_type_choice)
        .ok()
        .expect("ERR: Failed to read line.");

    let commit_choice_result = commit_type_choice.trim().parse::<i32>();
    let commit_choice: i32 = match commit_choice_result {
        Ok(commit_choice) => commit_choice - 1,
        Err(_e) => {
            println!(
                "{}ERR: Invalid number input.{}",
                color::Fg(color::Red),
                color::Fg(color::White)
            );
            process::exit(1);
        }
    };

    let mut title: String = String::new();

    if commit_choice == 6 {
        print!("\nTitle: ");
        io::stdout().flush().unwrap();
        io::stdin()
            .read_line(&mut title)
            .ok()
            .expect("ERR: Failed to read line.");
    } else {
        let commit_types: [&str; 6] = [
            "BUGFIX: ", "FEAT: ", "REFAC: ", "DOCS: ", "STYLE: ", "TEST: ",
        ];

        print!("\n{}", commit_types[commit_choice as usize]);
        io::stdout().flush().unwrap();
        io::stdin()
            .read_line(&mut title)
            .ok()
            .expect("ERR: Failed to read line.");

        title = format!("{}{}", commit_types[commit_choice as usize], title);
    }

    let mut body: String = String::new();
    print!("Enter the body of your commit (optional): ");
    io::stdout().flush().unwrap();
    io::stdin()
        .read_line(&mut body)
        .ok()
        .expect("ERR: Failed to read line.");

    return [title, body];
}

fn commit_verify(title: &String, body: &String) -> bool {
    let username: String;
    let email: String;
    unsafe {
        username = CONFIG.get_string("user.name").unwrap();
        email = CONFIG.get_string("user.email").unwrap();
    }

    println!(
        "
    {}
        {}
    author: {}
    email: {}
    ",
        title, body, username, email
    );

    print!("\nIs all the information above correct? [Y/n]: ");
    let mut verify_input: String = String::new();
    io::stdout().flush().unwrap();
    io::stdin()
        .read_line(&mut verify_input)
        .ok()
        .expect("ERR: Failed to read line.");
    verify_input = verify_input.trim().to_string();
    verify_input.make_ascii_lowercase();
    if ["", "y", "yes"].contains(&&verify_input[..]) {
        return true;
    }

    return false;
}

fn push(repo: &Repository) {
    let remote_name = choose_repo(repo);
    let mut remote: Remote = repo.find_remote(&remote_name).unwrap();
    // let url: &str = remote.pushurl().unwrap();

    let branch_name: &str = "temp";

    let refspec: String = format!("+refs/heads/{}:refs/remotes/{}", branch_name, remote_name);

    let remote_result = remote.push(&[refspec], Some(&mut PushOptions::default()));
    match remote_result {
        Ok(_remote) => {
            println!("{}  ➜ Successfullly pushed commit to {}{}", color::Fg(color::Green), remote_name, color::Fg(color::White));
        },
        Err(_e) => {
            println!("{}  x Unsuccessfully pushed commit to {}{}", color::Fg(color::Red), remote_name, color::Fg(color::White));
            process::exit(1);
        },
    };
}

fn choose_repo(repo: &Repository) -> String {
    let remotes_result: Result<StringArray, Error> = repo.remotes();
    let remotes = match remotes_result {
        Ok(remotes) => remotes,
        Err(_e) => {
            println!("{}ERR: No remotes were found for the git repository, please add one before trying to push.{}", color::Fg(color::Red), color::Fg(color::White));
            process::exit(123);
        }
    };

    let mut remotes_iter = remotes.into_iter();
    let mut i: i32 = 1;

    if remotes.len() == 0 {
        println!("{}ERR: No remotes were found for the git repository, please add one before trying to push.{}", color::Fg(color::Red), color::Fg(color::White));
        process::exit(123);
    } else if remotes.len() == 1 {
        let remote_name: &str = remotes_iter.next().unwrap().unwrap();
        println!(
            "{}  ➜ Remote to be used: {}{}",
            color::Fg(color::Green),
            remote_name,
            color::Fg(color::White)
        );
        return String::from(remote_name);
    }

    let mut remotes_arr = [];

    println!();
    for remote in remotes_iter {
        let name = remote.unwrap();
        let remote_info: Remote = repo.find_remote(remote.unwrap()).unwrap();
        println!("    [{}]: {} at {}", i, name, remote_info.url().unwrap());

        remotes_arr[i as usize] = name;
        i += 1;
    }

    print!("Which remote should be used? [1-{}]: ", i);
    io::stdout().flush().unwrap();
    let mut remote_choice: String = String::new();
    io::stdin()
        .read_line(&mut remote_choice)
        .ok()
        .expect("ERR: Failed to read line.");
    let remote_index_result = remote_choice.parse::<i32>();
    let remote_index = match remote_index_result {
        Ok(index) => index,
        Err(_e) => {
            println!("{}ERR: Input was not an integet{}", color::Fg(color::Red), color::Fg(color::White));
            process::exit(1);
        }
    };

    if remote_index > i && remote_index < 0 {
        println!("{}ERR: The Input number was not in the range of [1-{}]{}", color::Fg(color::Red), i, color::Fg(color::White));
        process::exit(1);
    }
    
    return String::from(remotes_arr[remote_index as usize]);
}
