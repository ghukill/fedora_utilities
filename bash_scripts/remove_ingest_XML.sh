for i in $(find . -type d -maxdepth 1)
do
    echo $
    mv $i/*.xml .
    rm -R $i
done
