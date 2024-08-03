export PATH_BAK=$PATH
export PATH=$JAVA11_HOME/bin:$PATH
cd dacapo
python3 test.py
cd ..

cd renaissance
python3 test.py
cd ..

export PATH=$PATH_BAK
export PATH=$JAVA8_HOME/bin:$PATH
cd spec/SPECjvm2008/
python3 test.py
cd ..

