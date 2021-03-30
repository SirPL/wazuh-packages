Summary:     Wazuh helps you to gain security visibility into your infrastructure by monitoring hosts at an operating system and application level. It provides the following capabilities: log analysis, file integrity monitoring, intrusions detection and policy and compliance monitoring
Name:        wazuh-manager
Version:     4.0.1
Release:     %{_release}
License:     GPL
Group:       System Environment/Daemons
Source0:     %{name}-%{version}.tar.gz
URL:         https://www.wazuh.com/
BuildRoot:   %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor:      Wazuh, Inc <info@wazuh.com>
Packager:    Wazuh, Inc <info@wazuh.com>
Requires(pre):    /usr/sbin/groupadd /usr/sbin/useradd
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/chkconfig /sbin/service
Requires(postun): /sbin/service /usr/sbin/groupdel /usr/sbin/userdel
Conflicts:   ossec-hids ossec-hids-agent wazuh-agent wazuh-local
Obsoletes: wazuh-api <= 3.13.2
AutoReqProv: no

Requires: coreutils
BuildRequires: coreutils glibc-devel automake autoconf libtool policycoreutils-python curl perl

ExclusiveOS: linux

%description
Wazuh helps you to gain security visibility into your infrastructure by monitoring
hosts at an operating system and application level. It provides the following capabilities:
log analysis, file integrity monitoring, intrusions detection and policy and compliance monitoring

%prep
%setup -q

./gen_ossec.sh conf manager centos %rhel %{_localstatedir} > etc/ossec-server.conf
./gen_ossec.sh init manager %{_localstatedir} > ossec-init.conf

%build
pushd src
# Rebuild for server
make clean

# Build Wazuh sources
make deps PREFIX=%{_localstatedir}
make -j%{_threads} TARGET=server USE_SELINUX=yes USE_FRAMEWORK_LIB=yes PREFIX=%{_localstatedir} DEBUG=%{_debugenabled}

popd

%install
# Clean BUILDROOT
rm -fr %{buildroot}

echo 'USER_LANGUAGE="en"' > ./etc/preloaded-vars.conf
echo 'USER_NO_STOP="y"' >> ./etc/preloaded-vars.conf
echo 'USER_INSTALL_TYPE="server"' >> ./etc/preloaded-vars.conf
echo 'USER_DIR="%{_localstatedir}"' >> ./etc/preloaded-vars.conf
echo 'USER_DELETE_DIR="y"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_ACTIVE_RESPONSE="y"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_SYSCHECK="y"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_ROOTCHECK="y"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_OPENSCAP="n"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_CISCAT="y"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_SYSCOLLECTOR="y"' >> ./etc/preloaded-vars.conf
echo 'USER_UPDATE="n"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_EMAIL="n"' >> ./etc/preloaded-vars.conf
echo 'USER_WHITE_LIST="n"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_SYSLOG="y"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_AUTHD="y"' >> ./etc/preloaded-vars.conf
echo 'USER_SERVER_IP="MANAGER_IP"' >> ./etc/preloaded-vars.conf
echo 'USER_CA_STORE="/path/to/my_cert.pem"' >> ./etc/preloaded-vars.conf
echo 'USER_GENERATE_AUTHD_CERT="y"' >> ./etc/preloaded-vars.conf
echo 'USER_AUTO_START="n"' >> ./etc/preloaded-vars.conf
echo 'USER_CREATE_SSL_CERT="n"' >> ./etc/preloaded-vars.conf
./install.sh

# Create directories
mkdir -p ${RPM_BUILD_ROOT}%{_initrddir}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/.ssh

# Copy the installed files into RPM_BUILD_ROOT directory
cp -pr %{_localstatedir}/* ${RPM_BUILD_ROOT}%{_localstatedir}/
mkdir -p ${RPM_BUILD_ROOT}/usr/lib/systemd/system/
install -m 0640 ossec-init.conf ${RPM_BUILD_ROOT}%{_sysconfdir}
install -m 0755 src/init/ossec-hids-rh.init ${RPM_BUILD_ROOT}%{_initrddir}/wazuh-manager
install -m 0644 src/systemd/wazuh-manager.service ${RPM_BUILD_ROOT}/usr/lib/systemd/system/

# Clean the preinstalled configuration assesment files
rm -f ${RPM_BUILD_ROOT}%{_localstatedir}/ruleset/sca/*

# Install Vulnerability Detector files
install -m 0440 src/wazuh_modules/vulnerability_detector/*.json ${RPM_BUILD_ROOT}%{_localstatedir}/queue/vulnerabilities/dictionaries

# Add configuration scripts
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/
cp gen_ossec.sh ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/
cp add_localfiles.sh ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/

# Templates for initscript
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/src/init
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/generic
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/centos
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/rhel

# Install configuration assesment files and files templates
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/{applications,generic}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/amzn/{1,2}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/centos/{7,6,5}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/{15,16,17,18}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/debian/{7,8,9}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu/{12,14,16}/04
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/rhel/{7,6,5}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/sles/{11,12}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/suse/{11,12}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/sunos
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/windows

cp -r etc/sca/{applications,generic,darwin,debian,rhel,sles,sunos,windows} ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp

cp etc/templates/config/generic/{sca.files,sca.manager.files} ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/generic

cp etc/templates/config/amzn/1/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/amzn/1
cp etc/templates/config/amzn/2/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/amzn/2

cp etc/templates/config/centos/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/centos
cp etc/templates/config/centos/6/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/centos/6
cp etc/templates/config/centos/5/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/centos/5

cp etc/templates/config/darwin/15/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/15
cp etc/templates/config/darwin/16/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/16
cp etc/templates/config/darwin/17/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/17
cp etc/templates/config/darwin/18/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/18

cp etc/templates/config/rhel/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/rhel
cp etc/templates/config/rhel/6/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/rhel/6
cp etc/templates/config/rhel/5/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/rhel/5

cp etc/templates/config/sles/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/sles
cp etc/templates/config/sles/11/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/sles/11

cp etc/templates/config/suse/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/suse
cp etc/templates/config/suse/11/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/suse/11

cp etc/templates/config/ubuntu/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu
cp etc/templates/config/ubuntu/12/04/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu/12/04
cp etc/templates/config/ubuntu/14/04/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu/14/04

cp etc/templates/config/debian/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/debian
cp etc/templates/config/debian/7/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/debian/7
cp etc/templates/config/debian/8/sca.files ${RPM_BUILD_ROOT}%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/debian/8

# Add SUSE initscript
cp -rp src/init/ossec-hids-suse.init ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/src/init/

# Copy scap templates
cp -rp  etc/templates/config/generic/* ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/generic
cp -rp  etc/templates/config/centos/* ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/centos
cp -rp  etc/templates/config/rhel/* ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/rhel

install -m 0640 src/init/*.sh ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/src/init

# Add installation scripts
cp src/VERSION ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/src/
cp src/REVISION ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/src/
cp src/LOCATION ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/src/

if [ %{_debugenabled} = "yes" ]; then
  %{_rpmconfigdir}/find-debuginfo.sh
fi
exit 0

%pre

# Create the ossec group if it doesn't exists
if command -v getent > /dev/null 2>&1 && ! getent group ossec > /dev/null 2>&1; then
  groupadd -r ossec
elif ! id -g ossec > /dev/null 2>&1; then
  groupadd -r ossec
fi

# Stop the services to upgrade the package
if [ $1 = 2 ]; then
  if command -v systemctl > /dev/null 2>&1 && systemctl > /dev/null 2>&1 && systemctl is-active --quiet wazuh-manager > /dev/null 2>&1; then
    systemctl stop wazuh-manager.service > /dev/null 2>&1
    touch %{_localstatedir}/tmp/wazuh.restart
  # Check for SysV
  elif command -v service > /dev/null 2>&1 && service wazuh-manager status 2>/dev/null | grep "is running" > /dev/null 2>&1; then
    service wazuh-manager stop > /dev/null 2>&1
    touch %{_localstatedir}/tmp/wazuh.restart
  elif %{_localstatedir}/bin/ossec-control status 2>/dev/null | grep "is running" > /dev/null 2>&1; then
    %{_localstatedir}/bin/ossec-control stop > /dev/null 2>&1
    touch %{_localstatedir}/tmp/wazuh.restart
  fi
fi

# Create the ossec user if it doesn't exists
if ! id -u ossec > /dev/null 2>&1; then
  useradd -g ossec -G ossec -d %{_localstatedir} -r -s /sbin/nologin ossec
fi
# Create the ossecr user if it doesn't exists
if ! id -u ossecr > /dev/null 2>&1; then
  useradd -g ossec -G ossec -d %{_localstatedir} -r -s /sbin/nologin ossecr
fi
# Create the ossecm user if it doesn't exists
if ! id -u ossecm > /dev/null 2>&1; then
  useradd -g ossec -G ossec -d %{_localstatedir} -r -s /sbin/nologin ossecm
fi

# Remove/relocate existing SQLite databases
rm -f %{_localstatedir}/var/db/cluster.db* || true
rm -f %{_localstatedir}/var/db/.profile.db* || true
rm -f %{_localstatedir}/var/db/agents/* || true

if [ -f %{_localstatedir}/var/db/global.db ]; then
  mv %{_localstatedir}/var/db/global.db %{_localstatedir}/queue/db/
  chmod 640 %{_localstatedir}/queue/db/global.db
  chown ossec:ossec %{_localstatedir}/queue/db/global.db
  rm -f %{_localstatedir}/var/db/global.db* || true
fi

# Remove Vuln-detector database
rm -f %{_localstatedir}/queue/vulnerabilities/cve.db || true

# Remove plain-text agent information if exists
if [ -d %{_localstatedir}/queue/agent-info ]; then
  rm -rf %{_localstatedir}/queue/agent-info/* > /dev/null 2>&1
fi

# Delete old API backups
if [ $1 = 2 ]; then
  if [ -d %{_localstatedir}/~api ]; then
    rm -rf %{_localstatedir}/~api
  fi
  # Import the variables from ossec-init.conf file
  . %{_sysconfdir}/ossec-init.conf

  # Get the major and minor version
  MAJOR=$(echo $VERSION | cut -dv -f2 | cut -d. -f1)
  MINOR=$(echo $VERSION | cut -d. -f2)

  # Delete uncompatible DBs versions
  if [ $MAJOR = 3 ] && [ $MINOR -lt 7 ]; then
    rm -f %{_localstatedir}/queue/db/*.db*
    rm -f %{_localstatedir}/queue/db/.template.db
  fi

  # Delete 3.X Wazuh API service
  if [ "$MAJOR" = "3" ] && [ -d %{_localstatedir}/api ]; then
    if command -v systemctl > /dev/null 2>&1 && systemctl > /dev/null 2>&1; then
      systemctl stop wazuh-api.service > /dev/null 2>&1
      systemctl disable wazuh-api.service > /dev/null 2>&1
      rm -f /etc/systemd/system/wazuh-api.service
    elif command -v service > /dev/null 2>&1 ; then
      service wazuh-api stop > /dev/null 2>&1
      chkconfig wazuh-api off > /dev/null 2>&1
      chkconfig --del wazuh-api > /dev/null 2>&1
      rm -f /etc/rc.d/init.d/wazuh-api || true
    fi
  fi
fi

%post

# Fresh install code block
if [ $1 = 1 ]; then
  sles=""
  if [ -f /etc/SuSE-release ]; then
    sles="suse"
  elif [ -f /etc/os-release ]; then
    if `grep -q "\"sles" /etc/os-release` ; then
      sles="suse"
    elif `grep -q -i "\"opensuse" /etc/os-release` ; then
      sles="opensuse"
    fi
  fi

  if [ ! -z "$sles" ]; then
    install -m 755 %{_localstatedir}/packages_files/manager_installation_scripts/src/init/ossec-hids-suse.init /etc/init.d/wazuh-manager
  fi

  . %{_localstatedir}/packages_files/manager_installation_scripts/src/init/dist-detect.sh

  # Generating ossec.conf file
  %{_localstatedir}/packages_files/manager_installation_scripts/gen_ossec.sh conf manager ${DIST_NAME} ${DIST_VER}.${DIST_SUBVER} %{_localstatedir} > %{_localstatedir}/etc/ossec.conf

  touch %{_localstatedir}/logs/active-responses.log
  touch %{_localstatedir}/logs/integrations.log
  chown ossec:ossec %{_localstatedir}/logs/active-responses.log
  chown ossecm:ossec %{_localstatedir}/logs/integrations.log
  chmod 0660 %{_localstatedir}/logs/active-responses.log
  chmod 0640 %{_localstatedir}/logs/integrations.log

  # Add default local_files to ossec.conf
  %{_localstatedir}/packages_files/manager_installation_scripts/add_localfiles.sh %{_localstatedir} >> %{_localstatedir}/etc/ossec.conf
fi

# Generation auto-signed certificate if not exists
if type openssl >/dev/null 2>&1 && [ ! -f "%{_localstatedir}/etc/sslmanager.key" ] && [ ! -f "%{_localstatedir}/etc/sslmanager.cert" ]; then
  openssl req -x509 -batch -nodes -days 365 -newkey rsa:2048 -subj "/C=US/ST=California/CN=Wazuh/" -keyout %{_localstatedir}/etc/sslmanager.key -out %{_localstatedir}/etc/sslmanager.cert 2>/dev/null
  chmod 640 %{_localstatedir}/etc/sslmanager.key
  chmod 640 %{_localstatedir}/etc/sslmanager.cert
fi

rm -f %{_localstatedir}/etc/shared/ar.conf  >/dev/null 2>&1
rm -f %{_localstatedir}/etc/shared/merged.mg  >/dev/null 2>&1

# CentOS
if [ -r "/etc/centos-release" ]; then
  DIST_NAME="centos"
  DIST_VER=`sed -rn 's/.* ([0-9]{1,2})\.*[0-9]{0,2}.*/\1/p' /etc/centos-release`
# Fedora
elif [ -r "/etc/fedora-release" ]; then
    DIST_NAME="generic"
    DIST_VER=""
# RedHat
elif [ -r "/etc/redhat-release" ]; then
  if grep -q "CentOS" /etc/redhat-release; then
      DIST_NAME="centos"
  else
      DIST_NAME="rhel"
  fi
  DIST_VER=`sed -rn 's/.* ([0-9]{1,2})\.*[0-9]{0,2}.*/\1/p' /etc/redhat-release`
# SUSE
elif [ -r "/etc/SuSE-release" ]; then
  if grep -q "openSUSE" /etc/SuSE-release; then
      DIST_NAME="generic"
      DIST_VER=""
  else
      DIST_NAME="sles"
      DIST_VER=`sed -rn 's/.*VERSION = ([0-9]{1,2}).*/\1/p' /etc/SuSE-release`
  fi
elif [ -r "/etc/os-release" ]; then
  . /etc/os-release
  DIST_NAME=$ID
  DIST_VER=$(echo $VERSION_ID | sed -rn 's/[^0-9]*([0-9]+).*/\1/p')
  if [ "X$DIST_VER" = "X" ]; then
      DIST_VER="0"
  fi
  if [ "$DIST_NAME" = "amzn" ] && [ "$DIST_VER" != "2" ]; then
      DIST_VER="1"
  fi
  DIST_SUBVER=$(echo $VERSION_ID | sed -rn 's/[^0-9]*[0-9]+\.([0-9]+).*/\1/p')
  if [ "X$DIST_SUBVER" = "X" ]; then
      DIST_SUBVER="0"
  fi
else
  DIST_NAME="generic"
  DIST_VER=""
fi

SCA_DIR="${DIST_NAME}/${DIST_VER}"
SCA_BASE_DIR="%{_localstatedir}/tmp/sca-%{version}-%{release}-tmp"
mkdir -p %{_localstatedir}/ruleset/sca

SCA_TMP_DIR="${SCA_BASE_DIR}/${SCA_DIR}"

# Install the configuration files needed for this hosts
if [ -r "${SCA_BASE_DIR}/${DIST_NAME}/${DIST_VER}/${DIST_SUBVER}/sca.files" ]; then
  SCA_TMP_DIR="${SCA_BASE_DIR}/${DIST_NAME}/${DIST_VER}/${DIST_SUBVER}"
elif [ -r "${SCA_BASE_DIR}/${DIST_NAME}/${DIST_VER}/sca.files" ]; then
  SCA_TMP_DIR="${SCA_BASE_DIR}/${DIST_NAME}/${DIST_VER}"
elif [ -r "${SCA_BASE_DIR}/${DIST_NAME}/sca.files" ]; then
  SCA_TMP_DIR="${SCA_BASE_DIR}/${DIST_NAME}"
else
  SCA_TMP_DIR="${SCA_BASE_DIR}/generic"
fi

SCA_TMP_FILE="${SCA_TMP_DIR}/sca.files"

if [ -r ${SCA_TMP_FILE} ] && [ -r ${SCA_BASE_DIR}/generic/sca.manager.files ]; then

  rm -f %{_localstatedir}/ruleset/sca/* || true

  for sca_file in $(cat ${SCA_TMP_FILE}); do
    if [ -f ${SCA_BASE_DIR}/${sca_file} ]; then
      mv ${SCA_BASE_DIR}/${sca_file} %{_localstatedir}/ruleset/sca
    fi
  done

  for sca_file in $(cat ${SCA_BASE_DIR}/generic/sca.manager.files); do
    filename=$(basename ${sca_file})
    if [ -f "${SCA_BASE_DIR}/${sca_file}" ] && [ ! -f "%{_localstatedir}/ruleset/sca/${filename}" ]; then
      mv ${SCA_BASE_DIR}/${sca_file} %{_localstatedir}/ruleset/sca/${filename}.disabled
    fi
  done
fi

# Fix sca permissions, group and owner
chmod 640 %{_localstatedir}/ruleset/sca/*
chown root:ossec %{_localstatedir}/ruleset/sca/*
# Delete the temporary directory
rm -rf ${SCA_BASE_DIR}

# Add the SELinux policy
if command -v getenforce > /dev/null 2>&1 && command -v semodule > /dev/null 2>&1; then
  if [ $(getenforce) != "Disabled" ]; then
    semodule -i %{_localstatedir}/var/selinux/wazuh.pp
    semodule -e wazuh
  fi
fi

# Delete the installation files used to configure the manager
rm -rf %{_localstatedir}/packages_files

# Remove unnecessary files from default group
rm -f %{_localstatedir}/etc/shared/default/*.rpmnew

%preun

if [ $1 = 0 ]; then

  # Stop the services before uninstall the package
  # Check for systemd
  if command -v systemctl > /dev/null 2>&1 && systemctl > /dev/null 2>&1 && systemctl is-active --quiet wazuh-manager > /dev/null 2>&1; then
    systemctl stop wazuh-manager.service > /dev/null 2>&1
  # Check for SysV
  elif command -v service > /dev/null 2>&1 && service wazuh-manager status 2>/dev/null | grep "running" > /dev/null 2>&1; then
    service wazuh-manager stop > /dev/null 2>&1
  else # Anything else
    %{_localstatedir}/bin/ossec-control stop > /dev/null 2>&1
  fi

  # Check for systemd
  if command -v systemctl > /dev/null 2>&1 && systemctl > /dev/null 2>&1; then
    systemctl disable wazuh-manager > /dev/null 2>&1
    systemctl daemon-reload > /dev/null 2>&1
  # Check for SysV
  elif command -v service > /dev/null 2>&1; then
    chkconfig wazuh-manager off > /dev/null 2>&1
    chkconfig --del wazuh-manager > /dev/null 2>&1
  fi

  # Remove the SELinux policy
  if command -v getenforce > /dev/null 2>&1 && command -v semodule > /dev/null 2>&1; then
    if [ $(getenforce) != "Disabled" ]; then
      if (semodule -l | grep wazuh > /dev/null); then
        semodule -r wazuh > /dev/null
      fi
    fi
  fi

  # Remove SCA files
  rm -f %{_localstatedir}/ruleset/sca/*
fi

%postun

# If the package is been uninstalled
if [ $1 = 0 ];then
  # Remove the ossecr user if it exists
  if id -u ossecr > /dev/null 2>&1; then
    userdel ossecr >/dev/null 2>&1
  fi
  # Remove the ossecm user if it exists
  if id -u ossecm > /dev/null 2>&1; then
    userdel ossecm >/dev/null 2>&1
  fi
  # Remove the ossec user if it exists
  if id -u ossec > /dev/null 2>&1; then
    userdel ossec >/dev/null 2>&1
  fi
  # Remove the ossec group if it exists
  if command -v getent > /dev/null 2>&1 && getent group ossec > /dev/null 2>&1; then
    groupdel ossec >/dev/null 2>&1
  elif id -g ossec > /dev/null 2>&1; then
    groupdel ossec >/dev/null 2>&1
  fi

  # Backup agents centralized configuration (etc/shared)
  if [ -d %{_localstatedir}/etc/shared ]; then
      rm -rf %{_localstatedir}/etc/shared.save/
      mv %{_localstatedir}/etc/shared/ %{_localstatedir}/etc/shared.save/
  fi

  # Backup registration service certificates (sslmanager.cert,sslmanager.key)
  if [ -f %{_localstatedir}/etc/sslmanager.cert ]; then
      mv %{_localstatedir}/etc/sslmanager.cert %{_localstatedir}/etc/sslmanager.cert.save
  fi
  if [ -f %{_localstatedir}/etc/sslmanager.key ]; then
      mv %{_localstatedir}/etc/sslmanager.key %{_localstatedir}/etc/sslmanager.key.save
  fi

  # Remove lingering folders and files
  rm -rf %{_localstatedir}/queue/
  rm -rf %{_localstatedir}/framework/
  rm -rf %{_localstatedir}/api/
  rm -rf %{_localstatedir}/stats/
  rm -rf %{_localstatedir}/var/
  rm -rf %{_localstatedir}/bin/
  rm -rf %{_localstatedir}/logs/
  rm -rf %{_localstatedir}/ruleset/
  rm -rf %{_localstatedir}/tmp
fi

# posttrans code is the last thing executed in a install/upgrade
%posttrans
if [ -f %{_localstatedir}/tmp/wazuh.restart ]; then
  rm -f %{_localstatedir}/tmp/wazuh.restart
  if command -v systemctl > /dev/null 2>&1 && systemctl > /dev/null 2>&1 ; then
    systemctl restart wazuh-manager.service > /dev/null 2>&1
  elif command -v service > /dev/null 2>&1; then
    service wazuh-manager restart > /dev/null 2>&1
  else
    %{_localstatedir}/bin/ossec-control restart > /dev/null 2>&1
  fi
fi

%triggerin -- glibc
[ -r %{_sysconfdir}/localtime ] && cp -fpL %{_sysconfdir}/localtime %{_localstatedir}/etc
 chown root:ossec %{_localstatedir}/etc/localtime
 chmod 0640 %{_localstatedir}/etc/localtime

%clean
rm -fr %{buildroot}

%files
%{_initrddir}/wazuh-manager
/usr/lib/systemd/system/wazuh-manager.service
%defattr(-,root,ossec)
%attr(640, root, ossec) %verify(not md5 size mtime) %{_sysconfdir}/ossec-init.conf
%dir %attr(750, root, ossec) %{_localstatedir}
%attr(750, root, ossec) %{_localstatedir}/agentless
%dir %attr(750, root, ossec) %{_localstatedir}/active-response
%dir %attr(750, root, ossec) %{_localstatedir}/active-response/bin
%attr(750, root, ossec) %{_localstatedir}/active-response/bin/*
%dir %attr(750, root, ossec) %{_localstatedir}/api
%dir %attr(770, root, ossec) %{_localstatedir}/api/configuration
%attr(660, root, ossec) %config(noreplace) %{_localstatedir}/api/configuration/api.yaml
%dir %attr(770, root, ossec) %{_localstatedir}/api/configuration/security
%dir %attr(770, root, ossec) %{_localstatedir}/api/configuration/ssl
%dir %attr(750, root, ossec) %{_localstatedir}/api/scripts
%attr(640, root, ossec) %{_localstatedir}/api/scripts/wazuh-apid.py
%dir %attr(750, root, ossec) %{_localstatedir}/backup
%dir %attr(750, ossec, ossec) %{_localstatedir}/backup/agents
%dir %attr(750, ossec, ossec) %{_localstatedir}/backup/groups
%dir %attr(750, root, ossec) %{_localstatedir}/backup/shared
%dir %attr(750, root, ossec) %{_localstatedir}/bin
%attr(750, root, root) %{_localstatedir}/bin/agent_control
%attr(750, root, ossec) %{_localstatedir}/bin/agent_groups
%attr(750, root, ossec) %{_localstatedir}/bin/agent_upgrade
%attr(750, root, root) %{_localstatedir}/bin/clear_stats
%attr(750, root, ossec) %{_localstatedir}/bin/cluster_control
%attr(750, root, root) %{_localstatedir}/bin/manage_agents
%attr(750, root, root) %{_localstatedir}/bin/ossec-agentlessd
%attr(750, root, root) %{_localstatedir}/bin/ossec-analysisd
%attr(750, root, root) %{_localstatedir}/bin/ossec-authd
%attr(750, root, root) %{_localstatedir}/bin/ossec-control
%attr(750, root, root) %{_localstatedir}/bin/ossec-csyslogd
%attr(750, root, root) %{_localstatedir}/bin/ossec-dbd
%attr(750, root, root) %{_localstatedir}/bin/ossec-execd
%attr(750, root, root) %{_localstatedir}/bin/ossec-integratord
%attr(750, root, root) %{_localstatedir}/bin/ossec-logcollector
%attr(750, root, root) %{_localstatedir}/bin/ossec-logtest
%attr(750, root, root) %{_localstatedir}/bin/ossec-maild
%attr(750, root, root) %{_localstatedir}/bin/ossec-makelists
%attr(750, root, root) %{_localstatedir}/bin/ossec-monitord
%attr(750, root, root) %{_localstatedir}/bin/ossec-regex
%attr(750, root, root) %{_localstatedir}/bin/ossec-remoted
%attr(750, root, root) %{_localstatedir}/bin/ossec-reportd
%attr(750, root, root) %{_localstatedir}/bin/ossec-syscheckd
%attr(750, root, root) %{_localstatedir}/bin/rootcheck_control
%attr(750, root, root) %{_localstatedir}/bin/syscheck_control
%attr(750, root, root) %{_localstatedir}/bin/syscheck_update
%attr(750, root, ossec) %{_localstatedir}/bin/update_ruleset
%attr(750, root, root) %{_localstatedir}/bin/util.sh
%attr(750, root, ossec) %{_localstatedir}/bin/verify-agent-conf
%attr(750, root, ossec) %{_localstatedir}/bin/wazuh-apid
%attr(750, root, ossec) %{_localstatedir}/bin/wazuh-clusterd
%attr(750, root, root) %{_localstatedir}/bin/wazuh-db
%attr(750, root, root) %{_localstatedir}/bin/wazuh-modulesd
%dir %attr(770, ossec, ossec) %{_localstatedir}/etc
%attr(660, root, ossec) %config(noreplace) %{_localstatedir}/etc/ossec.conf
%attr(640, root, ossec) %config(noreplace) %{_localstatedir}/etc/client.keys
%attr(640, root, ossec) %{_localstatedir}/etc/internal_options*
%attr(640, root, ossec) %config(noreplace) %{_localstatedir}/etc/local_internal_options.conf
%{_localstatedir}/etc/ossec-init.conf
%attr(640, root, ossec) %{_localstatedir}/etc/localtime
%dir %attr(770, root, ossec) %{_localstatedir}/etc/decoders
%attr(660, ossec, ossec) %config(noreplace) %{_localstatedir}/etc/decoders/local_decoder.xml
%dir %attr(770, root, ossec) %{_localstatedir}/etc/lists
%dir %attr(770, ossec, ossec) %{_localstatedir}/etc/lists/amazon
%attr(660, ossec, ossec) %config(noreplace) %{_localstatedir}/etc/lists/amazon/*
%attr(660, ossec, ossec) %config(noreplace) %{_localstatedir}/etc/lists/audit-keys
%attr(660, ossec, ossec) %config(noreplace) %{_localstatedir}/etc/lists/audit-keys.cdb
%attr(660, ossec, ossec) %config(noreplace) %{_localstatedir}/etc/lists/security-eventchannel
%attr(660, ossec, ossec) %config(noreplace) %{_localstatedir}/etc/lists/security-eventchannel.cdb
%dir %attr(770, root, ossec) %{_localstatedir}/etc/shared
%dir %attr(770, ossec, ossec) %{_localstatedir}/etc/shared/default
%attr(660, ossec, ossec) %{_localstatedir}/etc/shared/agent-template.conf
%attr(660, ossec, ossec) %config(noreplace) %{_localstatedir}/etc/shared/default/*
%dir %attr(770, root, ossec) %{_localstatedir}/etc/rootcheck
%attr(660, root, ossec) %{_localstatedir}/etc/rootcheck/*.txt
%dir %attr(770, root, ossec) %{_localstatedir}/etc/rules
%attr(660, ossec, ossec) %config(noreplace) %{_localstatedir}/etc/rules/local_rules.xml
%dir %attr(750, root, ossec) %{_localstatedir}/framework
%dir %attr(750, root, ossec) %{_localstatedir}/framework/python
%{_localstatedir}/framework/python/*
%dir %attr(750, root, ossec) %{_localstatedir}/framework/scripts
%attr(640, root, ossec) %{_localstatedir}/framework/scripts/*.py
%dir %attr(750, root, ossec) %{_localstatedir}/framework/wazuh
%attr(640, root, ossec) %{_localstatedir}/framework/wazuh/*.py
%dir %attr(750, root, ossec) %{_localstatedir}/framework/wazuh/core/cluster
%attr(640, root, ossec) %{_localstatedir}/framework/wazuh/core/cluster/*.py
%attr(640, root, ossec) %{_localstatedir}/framework/wazuh/core/cluster/*.json
%dir %attr(750, root, ossec) %{_localstatedir}/framework/wazuh/core/cluster/dapi
%attr(640, root, ossec) %{_localstatedir}/framework/wazuh/core/cluster/dapi/*.py
%dir %attr(750, root, ossec) %{_localstatedir}/integrations
%attr(750, root, ossec) %{_localstatedir}/integrations/*
%dir %attr(750, root, ossec) %{_localstatedir}/lib
%attr(750, root, ossec) %{_localstatedir}/lib/libwazuhext.so
%{_localstatedir}/lib/libpython3.8.so.1.0
%dir %attr(770, ossec, ossec) %{_localstatedir}/logs
%attr(660, ossec, ossec)  %ghost %{_localstatedir}/logs/active-responses.log
%attr(660, ossec, ossec) %ghost %{_localstatedir}/logs/api.log
%attr(640, ossecm, ossec) %ghost %{_localstatedir}/logs/integrations.log
%attr(660, ossec, ossec) %ghost %{_localstatedir}/logs/ossec.log
%attr(660, ossec, ossec) %ghost %{_localstatedir}/logs/ossec.json
%dir %attr(750, ossec, ossec) %{_localstatedir}/logs/api
%dir %attr(750, ossec, ossec) %{_localstatedir}/logs/archives
%dir %attr(750, ossec, ossec) %{_localstatedir}/logs/alerts
%dir %attr(750, ossec, ossec) %{_localstatedir}/logs/cluster
%dir %attr(750, ossec, ossec) %{_localstatedir}/logs/firewall
%dir %attr(750, ossec, ossec) %{_localstatedir}/logs/ossec
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/add_localfiles.sh
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/gen_ossec.sh
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/src/
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/src/LOCATION
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/src/REVISION
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/src/VERSION
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/src/init/
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/src/init/*
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/generic
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/generic/*
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/centos
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/centos/*
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/rhel
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/rhel/*
%dir %attr(750, root, ossec) %{_localstatedir}/queue
%attr(600, root, ossec) %ghost %{_localstatedir}/queue/agents-timestamp
%dir %attr(770, root, ossec) %{_localstatedir}/queue/agent-groups
%dir %attr(750, ossec, ossec) %{_localstatedir}/queue/agentless
%dir %attr(770, ossec, ossec) %{_localstatedir}/queue/alerts
%dir %attr(770, ossec, ossec) %{_localstatedir}/queue/cluster
%dir %attr(750, ossec, ossec) %{_localstatedir}/queue/db
%dir %attr(750, ossec, ossec) %{_localstatedir}/queue/diff
%dir %attr(750, ossec,ossec) %{_localstatedir}/queue/fim
%dir %attr(750, ossec,ossec) %{_localstatedir}/queue/fim/db
%dir %attr(750, ossec, ossec) %{_localstatedir}/queue/fts
%dir %attr(770, ossecr, ossec) %{_localstatedir}/queue/rids
%dir %attr(750, ossec, ossec) %{_localstatedir}/queue/rootcheck
%dir %attr(770, ossec, ossec) %{_localstatedir}/queue/ossec
%dir %attr(660, root, ossec) %{_localstatedir}/queue/vulnerabilities
%dir %attr(440, root, ossec) %{_localstatedir}/queue/vulnerabilities/dictionaries
%attr(0440, root, ossec) %{_localstatedir}/queue/vulnerabilities/dictionaries/cpe_helper.json
%attr(0440, root, ossec) %ghost %{_localstatedir}/queue/vulnerabilities/dictionaries/msu.json.gz
%dir %attr(750, root, ossec) %{_localstatedir}/ruleset
%dir %attr(750, root, ossec) %{_localstatedir}/ruleset/sca
%attr(640, root, ossec) %{_localstatedir}/ruleset/VERSION
%dir %attr(750, root, ossec) %{_localstatedir}/ruleset/decoders
%attr(640, root, ossec) %{_localstatedir}/ruleset/decoders/*
%dir %attr(750, root, ossec) %{_localstatedir}/ruleset/rules
%attr(640, root, ossec) %{_localstatedir}/ruleset/rules/*
%dir %attr(770, root, ossec) %{_localstatedir}/.ssh
%dir %attr(750, ossec, ossec) %{_localstatedir}/stats
%dir %attr(1770, root, ossec) %{_localstatedir}/tmp
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/applications
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/applications/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/generic
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/generic/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/amzn
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/amzn/1
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/amzn/1/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/amzn/2
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/amzn/2/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/centos
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/centos/sca.files
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/centos/5
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/centos/5/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/centos/6
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/centos/6/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/centos/7
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/15
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/15/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/16
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/16/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/17
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/17/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/18
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/darwin/18/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/debian
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/debian/sca.files
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/debian/*yml
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/debian/7
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/debian/7/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/debian/8
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/debian/8/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/debian/9
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/rhel
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/rhel/sca.files
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/rhel/5
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/rhel/5/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/rhel/6
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/rhel/6/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/rhel/7
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/rhel/7/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/sles
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/sles/sca.files
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/sles/11
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/sles/11/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/sles/12
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/sles/12/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/sunos
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/sunos/*
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/suse/sca.files
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/suse/11
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/suse/11/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/suse/12
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu/sca.files
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu/12
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu/12/04
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu/12/04/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu/14
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu/14/04
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu/14/04/*
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu/16
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/ubuntu/16/04
%dir %attr(750, ossec, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/windows
%attr(640, root, ossec) %config(missingok) %{_localstatedir}/tmp/sca-%{version}-%{release}-tmp/windows/*
%dir %attr(750, root, ossec) %{_localstatedir}/var
%dir %attr(770, root, ossec) %{_localstatedir}/var/db
%dir %attr(770, root, ossec) %{_localstatedir}/var/db/agents
%attr(660, root, ossec) %{_localstatedir}/var/db/mitre.db
%dir %attr(770, root, ossec) %{_localstatedir}/var/download
%dir %attr(770, ossec, ossec) %{_localstatedir}/var/multigroups
%dir %attr(770, root, ossec) %{_localstatedir}/var/run
%dir %attr(770, root, ossec) %{_localstatedir}/var/selinux
%attr(640, root, ossec) %{_localstatedir}/var/selinux/*
%dir %attr(770, root, ossec) %{_localstatedir}/var/upgrade
%dir %attr(770, root, ossec) %{_localstatedir}/var/wodles
%dir %attr(750, root, ossec) %{_localstatedir}/wodles
%dir %attr(750, root, ossec) %{_localstatedir}/wodles/aws
%attr(750, root, ossec) %{_localstatedir}/wodles/aws/*
%dir %attr(750, root, ossec) %{_localstatedir}/wodles/azure
%attr(750, root, ossec) %{_localstatedir}/wodles/azure/*
%dir %attr(750, root, ossec) %{_localstatedir}/wodles/docker
%attr(750, root, ossec) %{_localstatedir}/wodles/docker/*
%dir %attr(750, root, ossec) %{_localstatedir}/wodles/gcloud
%attr(750, root, ossec) %{_localstatedir}/wodles/gcloud/*

%if %{_debugenabled} == "yes"
/usr/lib/debug/%{_localstatedir}/*
/usr/src/debug/%{name}-%{version}/*
%endif


%changelog
* Sat Oct 31 2020 support <info@wazuh.com> - 4.0.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Oct 19 2020 support <info@wazuh.com> - 4.0.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Fri Aug 21 2020 support <info@wazuh.com> - 3.13.2
- More info: https://documentation.wazuh.com/current/release-notes/
* Tue Jul 14 2020 support <info@wazuh.com> - 3.13.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Jun 29 2020 support <info@wazuh.com> - 3.13.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed May 13 2020 support <info@wazuh.com> - 3.12.3
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu Apr 9 2020 support <info@wazuh.com> - 3.12.2
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Apr 8 2020 support <info@wazuh.com> - 3.12.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Mar 25 2020 support <info@wazuh.com> - 3.12.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Feb 24 2020 support <info@wazuh.com> - 3.11.4
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Jan 22 2020 support <info@wazuh.com> - 3.11.3
- More info: https://documentation.wazuh.com/current/release-notes/
* Tue Jan 7 2020 support <info@wazuh.com> - 3.11.2
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu Dec 26 2019 support <info@wazuh.com> - 3.11.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Oct 7 2019 support <info@wazuh.com> - 3.11.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Sep 23 2019 support <info@wazuh.com> - 3.10.2
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu Sep 19 2019 support <info@wazuh.com> - 3.10.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Aug 26 2019 support <info@wazuh.com> - 3.10.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu Aug 8 2019 support <info@wazuh.com> - 3.9.5
- More info: https://documentation.wazuh.com/current/release-notes/
* Fri Jul 12 2019 support <info@wazuh.com> - 3.9.4
- More info: https://documentation.wazuh.com/current/release-notes/
* Tue Jun 11 2019 support <info@wazuh.com> - 3.9.3
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu Jun 6 2019 support <info@wazuh.com> - 3.9.2
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon May 6 2019 support <info@wazuh.com> - 3.9.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Feb 25 2019 support <info@wazuh.com> - 3.9.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Jan 30 2019 support <info@wazuh.com> - 3.8.2
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu Jan 24 2019 support <info@wazuh.com> - 3.8.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Jan 16 2019 support <info@wazuh.com> - 3.8.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Dec 10 2018 support <info@wazuh.com> - 3.7.2
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Nov 12 2018 support <info@wazuh.com> - 3.7.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Sat Nov 10 2018 support <info@wazuh.com> - 3.7.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Sep 3 2018 support <info@wazuh.com> - 3.6.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu Aug 23 2018 support <support@wazuh.com> - 3.6.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Jul 25 2018 support <support@wazuh.com> - 3.5.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Jul 11 2018 support <support@wazuh.com> - 3.4.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Jun 18 2018 support <support@wazuh.com> - 3.3.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Jun 11 2018 support <support@wazuh.com> - 3.3.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed May 30 2018 support <support@wazuh.com> - 3.2.4
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu May 10 2018 support <support@wazuh.com> - 3.2.3
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Apr 09 2018 support <support@wazuh.com> - 3.2.2
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Feb 21 2018 support <support@wazuh.com> - 3.2.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Feb 07 2018 support <support@wazuh.com> - 3.2.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Tue Dec 19 2017 support <support@wazuh.com> - 3.1.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Nov 06 2017 support <support@wazuh.com> - 3.0.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Tue Jun 06 2017 support <support@wazuh.com> - 2.0.1
- Changed random data generator for a secure OS-provided generator.
- Changed Windows installer file name (depending on version).
- Linux distro detection using standard os-release file.
- Changed some URLs to documentation.
- Disable synchronization with SQLite databases for Syscheck by default.
- Minor changes at Rootcheck formatter for JSON alerts.
- Added debugging messages to Integrator logs.
- Show agent ID when possible on logs about incorrectly formatted messages.
- Use default maximum inotify event queue size.
- Show remote IP on encoding format errors when unencrypting messages.
- Fix permissions in agent-info folder
- Fix permissions in rids folder.
* Fri Apr 21 2017 Jose Luis Ruiz <jose@wazuh.com> - 2.0
- Changed random data generator for a secure OS-provided generator.
- Changed Windows installer file name (depending on version).
- Linux distro detection using standard os-release file.
- Changed some URLs to documentation.
- Disable synchronization with SQLite databases for Syscheck by default.
- Minor changes at Rootcheck formatter for JSON alerts.
- Added debugging messages to Integrator logs.
- Show agent ID when possible on logs about incorrectly formatted messages.
- Use default maximum inotify event queue size.
- Show remote IP on encoding format errors when unencrypting messages.
- Fixed resource leaks at rules configuration parsing.
- Fixed memory leaks at rules parser.
- Fixed memory leaks at XML decoders parser.
- Fixed TOCTOU condition when removing directories recursively.
- Fixed insecure temporary file creation for old POSIX specifications.
- Fixed missing agentless devices identification at JSON alerts.
- Fixed FIM timestamp and file name issue at SQLite database.
- Fixed cryptographic context acquirement on Windows agents.
- Fixed debug mode for Analysisd.
- Fixed bad exclusion of BTRFS filesystem by Rootcheck.
- Fixed compile errors on macOS.
- Fixed option -V for Integrator.
- Exclude symbolic links to directories when sending FIM diffs (by Stephan Joerrens).
- Fixed daemon list for service reloading at ossec-control.
- Fixed socket waiting issue on Windows agents.
- Fixed PCI_DSS definitions grouping issue at Rootcheck controls.