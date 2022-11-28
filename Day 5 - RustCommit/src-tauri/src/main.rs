#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use git2::string_array::StringArray;
use git2::Commit;
use git2::Error;
use git2::PushOptions;
use git2::Reference;
use git2::Remote;
use git2::Repository;
use git2::Signature;
use git2::Tree;

static mut REPOSITORY: Option<Repository> = None;

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            open_repo,
            stage_all,
            commit,
            get_remotes,
            push
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[tauri::command]
fn open_repo(path: &str) -> bool {
    match Repository::open(path) {
        Ok(repo) => {
            unsafe {
                REPOSITORY = Some(repo);
            }
            return true;
        }
        Err(_e) => {
            unsafe {
                REPOSITORY = None;
            }
            return false;
        }
    };
}

#[tauri::command]
fn stage_all() -> bool {
    unsafe {
        if let None = REPOSITORY {
            return false;
        }
        let mut index = REPOSITORY.as_mut().unwrap().index().unwrap();
        index
            .add_all(&["."], git2::IndexAddOption::DEFAULT, None)
            .unwrap();
        return match index.write() {
            Ok(..) => true,
            Err(..) => false,
        };
    }
}

#[tauri::command]
fn commit(title: &str, body: &str) -> i32 {
    let config_result = git2::Config::open_default();
    let config = match config_result {
        Ok(config) => config,
        Err(_) => return 1,
    };

    let signature: Signature = Signature::now(
        &config.get_string("user.name").unwrap()[..],
        &config.get_string("user.email").unwrap()[..],
    )
    .unwrap();

    unsafe {
        let oid = REPOSITORY
            .as_mut()
            .unwrap()
            .index()
            .unwrap()
            .write_tree()
            .unwrap();
        let tree: Tree = REPOSITORY.as_mut().unwrap().find_tree(oid).unwrap();

        let head_result: Result<Reference, Error> = REPOSITORY.as_mut().unwrap().head();
        let has_head = match head_result {
            Ok(_head) => true,
            Err(_e) => false,
        };

        if has_head {
            let parent_commit_result: Result<Commit, Error> = REPOSITORY
                .as_mut()
                .unwrap()
                .head()
                .unwrap()
                .peel_to_commit();
            let mut has_parent: bool = false;
            match parent_commit_result {
                Ok(_commit) => {
                    has_parent = true;
                }
                Err(_e) => {}
            };

            if has_parent {
                let parent_commit = &[&REPOSITORY
                    .as_mut()
                    .unwrap()
                    .head()
                    .unwrap()
                    .peel_to_commit()
                    .unwrap()];
                REPOSITORY
                    .as_mut()
                    .unwrap()
                    .commit(
                        Some("HEAD"),
                        &signature,
                        &signature,
                        &format!("{}\n\n{}", title, body)[..],
                        &tree,
                        parent_commit,
                    )
                    .unwrap();
            } else {
                REPOSITORY
                    .as_mut()
                    .unwrap()
                    .commit(
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
            REPOSITORY
                .as_mut()
                .unwrap()
                .commit(
                    Some("HEAD"),
                    &signature,
                    &signature,
                    &format!("{}\n\n{}", title, body)[..],
                    &tree,
                    &[],
                )
                .unwrap();
        }
    }

    return 0;
}

#[tauri::command]
fn get_remotes() -> Vec<String> {
    let mut return_vec: Vec<String> = Vec::new();

    let remotes;
    unsafe {
        let remotes_result: Result<StringArray, Error> = REPOSITORY.as_mut().unwrap().remotes();
        remotes = match remotes_result {
            Ok(remotes) => remotes,
            Err(_e) => {
                return_vec.push(String::from("1"));
                return return_vec;
            }
        };
    }

    let mut remotes_iter = remotes.into_iter();

    if remotes.len() == 0 {
        return_vec.push(String::from("1"));
        return return_vec;
    } else if remotes.len() == 1 {
        return_vec.push(remotes_iter.next().unwrap().unwrap().to_string());
        return return_vec;
    } else {
        let mut remotes_arr = Vec::new();

        for remote in remotes_iter {
            let name = remote.unwrap();
            remotes_arr.push(name);
            return_vec.push(name.to_string());
        }

        return return_vec;
    }
}

#[tauri::command]
fn push(remote_name: &str) -> bool {
    let mut remote: Remote;
    unsafe {
        remote = REPOSITORY
            .as_mut()
            .unwrap()
            .find_remote(&remote_name)
            .unwrap();
    }

    let branch_name: &str = "day-5"; // temporary will be replaced with similar solution to cli

    let refspec: String = format!("+refs/heads/{}:refs/remotes/{}", branch_name, remote_name);

    let remote_result = remote.push(&[refspec], Some(&mut PushOptions::default()));
    match remote_result {
        Ok(_remote) => {
            return true;
        }
        Err(_e) => {
            return false;
        }
    };
}
