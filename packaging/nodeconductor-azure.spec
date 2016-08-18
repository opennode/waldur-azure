Name: nodeconductor-azure
Summary: NodeConductor plugin for managing MS Azure resources.
Group: Development/Libraries
Version: 0.2.0
Release: 1.el7
License: MIT
Url: http://nodeconductor.com
Source0: %{name}-%{version}.tar.gz

Requires: nodeconductor > 0.102.2
Requires: python-libcloud >= 0.20.1
Requires: python-cryptography

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires: python-setuptools

%description
NodeConductor plugin for managing MS Azure resources.

%prep
%setup -q -n %{name}-%{version}

%build
python setup.py build

%install
rm -rf %{buildroot}
python setup.py install --single-version-externally-managed -O1 --root=%{buildroot} --record=INSTALLED_FILES

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Thu Jun 30 2016 Jenkins <jenkins@opennodecloud.com> - 0.2.0-1.el7
- New upstream release

* Mon Jun 27 2016 Jenkins <jenkins@opennodecloud.com> - 0.1.0-1.el7
- New upstream release

* Mon May 9 2016 Victor Mireyev <victor@opennodecloud.com> - 0.1.0-1.el7
- Initial version of the package

