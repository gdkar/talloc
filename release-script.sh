#!/bin/bash

if [ "$1" = "" ]; then
    echo "Please provide version string, eg: 1.2.0"
    exit 1
fi

if [ ! -d "lib/talloc" ]; then
    echo "Run this script from the samba base directory."
    exit 1
fi

curbranch=`git-branch |grep "^*" | tr -d "* "`

version=$1
strver=`echo ${version} | tr "." "-"`

# Checkout the release tag
git branch -f talloc-release-script-${strver} talloc-${strver}
if [ ! "$?" = "0" ];  then
    echo "Unable to checkout talloc-${strver} release"
    exit 1
fi

git checkout talloc-release-script-${strver}

# Test configure agrees with us
confver=`grep "^AC_INIT" lib/talloc/configure.ac | tr -d "AC_INIT(talloc, " | tr -d ")"`
if [ ! "$confver" = "$version" ]; then
    echo "Wrong version, requested release for ${version}, found ${confver}"
    exit 1
fi

# Now build tarball
cp -a lib/talloc talloc-${version}
cp -a lib/replace talloc-${version}/libreplace
pushd talloc-${version}
./autogen.sh
popd
tar cvzf talloc-${version}.tar.gz talloc-${version}
rm -fr talloc-${version}

#Clean up
git checkout $curbranch
git branch -d talloc-release-script-${strver}
