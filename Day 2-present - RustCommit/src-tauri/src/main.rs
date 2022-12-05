#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use git2::string_array::StringArray;
use git2::BranchType;
use git2::Branches;
use git2::Commit;
use git2::Error;
use git2::PushOptions;
use git2::Reference;
use git2::Remote;
use git2::Repository;
use git2::Signature;
use git2::Tree;

use tauri::{AboutMetadata, CustomMenuItem, Menu, MenuItem, Submenu};

use once_cell::sync::Lazy;

static mut REPOSITORY: Option<Repository> = None;

static VERSION: Lazy<String> = Lazy::new(|| String::from("0.1.0"));

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            open_repo,
            stage_all,
            commit,
            get_remotes,
            push,
            get_branches,
        ])
        .menu(
            Menu::new()
                .add_submenu(Submenu::new(
                    "File",
                    Menu::new()
                        .add_item(
                            CustomMenuItem::new("settings", "Settings")
                                .accelerator("cmdOrControl+,"),
                        )
                        .add_native_item(MenuItem::Separator)
                        .add_native_item(MenuItem::Quit),
                ))
                .add_submenu(Submenu::new(
                    "Git",
                    Menu::new()
                        .add_item(CustomMenuItem::new("open_repo", "Open Repo"))
                        .add_item(CustomMenuItem::new(
                            "default_branch",
                            "Select Default Branch",
                        ))
                        .add_item(CustomMenuItem::new("stage", "Stage Changes"))
                        .add_item(CustomMenuItem::new("commit", "Commit"))
                        .add_item(CustomMenuItem::new(
                            "default_remote",
                            "Select Default Remote",
                        ))
                        .add_item(CustomMenuItem::new("push", "Push to remote")),
                ))
                .add_submenu(Submenu::new(
                    "About",
                    Menu::new()
                        .add_native_item(MenuItem::About(
                            String::from("RustCommit"),
                            AboutMetadata::new()
                                .version(&*VERSION)
                                .authors(vec![String::from("Antoine Meloche")])
                                .copyright(String::from("Copyright 2022 © Antoine Meloche"))
                                .license(String::from("GPL-v3"))
                                .website(String::from(
                                    "https://github.com/Antoine-Meloche/Coding365",
                                ))
                                .website_label(String::from("Source Code")),
                        )),
                )),
        )
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
fn get_branches() -> Vec<String> {
    let mut return_vec: Vec<String> = Vec::new();

    let branches;
    unsafe {
        let branches_result: Result<Branches, Error> = REPOSITORY
            .as_mut()
            .unwrap()
            .branches(Some(BranchType::Local));
        branches = match branches_result {
            Ok(branches) => branches,
            Err(_e) => {
                return_vec.push(String::from("1"));
                return return_vec;
            }
        };
    }

    let branches_iter = branches.into_iter();

    for branch in branches_iter {
        let name = branch.unwrap().0.name().unwrap().unwrap().to_string();
        return_vec.push(name);
    }

    return return_vec;
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
fn push(remote_name: &str, branch_name: &str) -> bool {
    let mut remote: Remote;
    unsafe {
        remote = REPOSITORY
            .as_mut()
            .unwrap()
            .find_remote(&remote_name)
            .unwrap();
    }

    unsafe {
        let upstream_branch_result = REPOSITORY.branch_upstream_name(branch_name);
        match upstream_branch_result {
            Ok(upstream_branch_name) => {
                branch_name = upstream_branch_name.as_str().unwrap();
            },
            Err(_) => {
                Branch::wrap(resolve_reference_from_short_name(branch_name)).set_upstream(Some(branch_name));
            }
        }
    }

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

#[derive(Default)]
fn checkout(branch_name: &str) -> bool {
    unsafe {
        let (object, reference) = REPOSITORY.revparse_ext(branch_name).expect("Object not found");
        
        REPOSITORY.checkout_tree(&object, None)
            .expect("Failed to checkout");
    
        match reference {
            Some(gref) => REPOSITORY.set_head(gref.name().unwrap()),
            None => REPOSITORY.set_head_detached(object.id()),
        }
        .expect("Failed to set HEAD");
    }
}