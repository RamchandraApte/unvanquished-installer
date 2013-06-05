cd dist &&
tar -c . > ../installer.tar &&
cd .. &&
python3.3 gen_tar_data.py &&
cxfreeze tar_dec.py --target-dir tar_dec_dist --include-modules=installer &&
tar_dec_dist/tar_dec