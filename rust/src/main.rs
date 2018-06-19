extern crate csv;
extern crate sha1;
extern crate rayon;

use std::collections::HashSet;
use std::env::args;
use std::error::Error;
use std::fs::File;
use std::path::PathBuf;
use std::process;
use std::time::Instant;

use csv::ReaderBuilder;
use rayon::prelude::*;


const FILES: [&str; 4] = [
    "DEF-9x.csv",
    "ABC-8x.csv",
    "ABC-3x.csv",
    "ABC-4x.csv"
];
type Record = (u16, u32, u32, u32, String, String);


fn get_base_path() -> Result<(PathBuf), Box<Error>> {
    let current_exe = std::env::current_exe()?;
    if let Some(current_dir) = current_exe.parent() {
        let base_path = current_dir.join("../../..").canonicalize()?;
        return Ok(base_path)
    }
    Err(From::from("Can't resolve base path"))
}


fn get_wanted_hashes() -> Result<HashSet<String>, String> {
    let wanted_hashes: HashSet<String> = args().skip(1).collect();
    if wanted_hashes.is_empty() {
        return Err(From::from("Expected hashes, got none"))
    }
    Ok(wanted_hashes)
}


fn check_hashes(record: Record, wanted: &HashSet<String>) -> HashSet<String> {
    let (code, start, end, ..) = record;
    (start..end + 1).into_par_iter().filter_map(|number| {
        let phone_number = format!("7{}{:07}", code, number);
        let phone_hash = sha1::Sha1::from(&phone_number).digest().to_string();
        if wanted.contains(&phone_hash) {
            println!("PHONE:{} {}", phone_number, phone_hash);
            return Some(phone_hash)
        }
        return None
    }).collect()
}


fn scan_file(
    filename: &str, wanted: &HashSet<String>, found: &mut HashSet<String>
) -> Result<bool, Box<Error>> {
    let base_path = get_base_path()?;
    let file = File::open(base_path.join("registry").join(&filename))?;
    let mut rdr = ReaderBuilder::new().flexible(true).delimiter(b';').from_reader(file);
    println!("FILE:{}", filename);
    for result in rdr.deserialize() {
        let record: Record = result?;
        let checked_hashes = check_hashes(record, &wanted);
        found.extend(checked_hashes);
        if found.is_superset(&wanted) {
            return Ok(true)
        }
    }
    return Ok(false)
}


fn run() -> Result<(), Box<Error>> {
    let wanted_hashes = get_wanted_hashes()?;
    let mut found_hashes: HashSet<String> = HashSet::new();
    for filename in FILES.iter() {
        if scan_file(filename, &wanted_hashes, &mut found_hashes)? {
            return Ok(())
        }
    }
    for phone in wanted_hashes.difference(&found_hashes) {
        println!("UNKNOWN:{}", phone);
    }
    Ok(())
}


fn main() {
    let start = Instant::now();
    if let Err(err) = run() {
        println!("ERROR:{}", err);
        process::exit(1);
    }
    println!("RUNTIME:{}", start.elapsed().as_secs());
}
