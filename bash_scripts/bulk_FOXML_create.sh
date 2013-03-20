for i in $(find /var/www/data -type d -maxdepth 1)
do
    echo $
    python ebook_ingest.py $i ramsey
done