# PCTools

## Dependencies

```
$ mkdir -p $HOME/opt/pctools
$ virtualenv --system-site-packages -p /usr/bin/python3 $HOME/opt/pctools
```

### LASzip

```
$ git clone https://github.com/LASzip/LASzip
$ cd LASzip
$ mkdir build
$ cd build
$ cmake .. -DCMAKE_INSTALL_PREFIX=/home/user/opt/pctools
$ make
$ make install
```

### PgPointCloud

```
$ git clone https://github.com/pgpointcloud/pointcloud
$ cd pointcloud
$ ./autogen.sh
$ ./configure
$ make
$ make install
```

### PDAL

```
$ git clone https://github.com/PDAL/PDAL
$ cd PDAL
$ mkdir build
$ cd build
$ cmake .. -DLASZIP_INCLUDE_DIR=/home/user/opt/pctools/include \
    -DLASZIP_LIBRARY=/home/user/opt/pctools/lib/liblaszip.so \
    -DCMAKE_INSTALL_PREFIX=/home/user/opt/pctools
$ make
$ make install
```

```
$ git clone https://github.com/PDAL/python PDAL_python
$ cd PDAL_python
$ source $USER/opt/pctools/bin/activate
(pctools)$ pip intall Cython packaging
(pctools)$ python setup.py install --root=/home/user/opt/ --prefix=pctools
```

## Test installation

```
(pctools)$ export PCTOOLS=$USER/opt/pctools
(pctools)$ export LD_LIBRARY_PATH=$PCTOOLS/lib:$PCTOOLS/lib/python3.5/site-packages/pdal
(pctools)$ export PATH=$PCTOOLS/bin
(pctools)$ export PYTHONPATH=$PCTOOLS/lib/python3.5/site-packages/
(pctools)$ python
Python 3.5.2+ (default, Sep 22 2016, 12:18:14)
[GCC 6.2.0 20160927] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pdal
>>>
```

Then, you should activate the PCTool virtualenv before running QGIS.

## Create database

```
$ createdb pctools
$ psql pctools
pctools=# create extension postgis;
CREATE EXTENSION
pctools=# create extension pointcloud;
CREATE EXTENSION
pctools=# create extension pointcloud_postgis;
CREATE EXTENSION
```

Then init Postgis connection with `pctools` database in QGIS.
