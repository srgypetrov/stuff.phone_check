extern crate csv;
extern crate sha1;
extern crate rayon;

use std::collections::HashSet;
use std::env::args;
use std::error::Error;
use std::fs::File;
use std::process;
use std::time::Instant;

use csv::ReaderBuilder;
use rayon::prelude::*;


fn get_wanted_hashes() -> Result<HashSet<String>, String> {
    let wanted_hashes: HashSet<String> = args().skip(1).collect();
    if wanted_hashes.is_empty() {
        return Err(From::from("Expected hashes, got none"))
    }
    Ok(wanted_hashes)
}


fn run() -> Result<(), Box<Error>> {
    let wanted_hashes = get_wanted_hashes()?;
    let mut found_hashes: HashSet<String> = HashSet::new();
    let files = ["DEF-9x.csv", "ABC-8x.csv", "ABC-3x.csv", "ABC-4x.csv"];
    for filename in &files {
        let file = File::open(filename)?;
        let mut rdr = ReaderBuilder::new().flexible(true).delimiter(b';').from_reader(file);
        for result in rdr.records() {
            let record = result?;
            let code = record.get(0).unwrap();
            let start: i32 = record.get(1).unwrap().parse().unwrap();
            let end: i32 = record.get(2).unwrap().parse().unwrap();
            let checked_hashes: HashSet<String> = (start..end + 1).into_par_iter().map(|number| {
                let pnumber = format!("7{}{:07}", code, number);
                let phash = sha1::Sha1::from(&pnumber).digest().to_string();
                if wanted_hashes.contains(&phash) {
                    println!("PHONE: {}", pnumber);
                    return Some(phash)
                }
                return None
            }).filter_map(|x| x).collect();
            found_hashes.extend(checked_hashes);
            if found_hashes.is_superset(&wanted_hashes) {
                return Ok(())
            }
        }
    }
    for phone in wanted_hashes.difference(&found_hashes) {
        println!("UNKNOWN: {}", phone);
    }
    Ok(())
}


fn main() {
    let start = Instant::now();
    if let Err(err) = run() {
        println!("ERROR: {}", err);
        process::exit(1);
    }
    println!("RUNTIME: {}", start.elapsed().as_secs());
}
