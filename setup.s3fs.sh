# install s3fs on amazon linux
sudo yum -y update
sudo yum -y install automake fuse fuse-devel gcc-c++ git libcurl-devel libxml2-devel make openssl-devel
git clone https://github.com/s3fs-fuse/s3fs-fuse.git

cd  s3fs-fuse
./autogen.sh
./configure -prefix=/usr -with-openssl
make
sudo make install
