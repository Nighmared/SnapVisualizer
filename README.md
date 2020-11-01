# SnapVisualizer

[TOC]

## Requirements

- matplotlib
  - `pip install matplotlib`



## HOW-TO

- [ ] go to [Snap Accounts Website](accounts.snapchat.com)

- [ ] click on "my data"

- [ ] request your data at bottom of page

- [ ] wait &approx; 2h for the download to be available

- [ ] download archive

- [ ] unzip

- [ ] either:

  - copy/move the following files in the same directory as`analyse.py`

    - `[archive directory]/json/snap_history.json`

    - `[archive directory]/json/chat_history.json` 
    - run `python3 analyse.py` 

  - run `python3 analyse.py --dir /path/to/json/files`

- [ ] 2 new Files (will appear in json directory): 

  - [ ] > pieExport.png

  - [ ] > snapExport.csv



## Example

```bash
$python3 analyse.py --showcase --dir ~/Downloads/snapstats --o .
[Warning] chat_history.json not found -> ignoring
$ls
analyse.py  pieExport.png  README.md  snapExport.csv
```



![pieExport.png](/home/nighmared/Documents/GitHub Repos/SnapVisualizer/pieExport.png)