for i in $(find /var/www/data -type d -maxdepth 1)
do
    echo $i
    java -jar saxon9he.jar $i/*_FOXML.xml ebook_FOXEYMOLE_creator_v2.xsl
done
