Name: waldur-azure
Summary: Waldur plugin for managing MS Azure resources.
Group: Development/Libraries
Version: 0.3.5
Release: 1.el7
License: MIT
Url: https://waldur.com
Source0: %{name}-%{version}.tar.gz

Requires: waldur-core >= 0.157.5
Requires: python-libcloud >= 1.1.0
Requires: python-libcloud < 2.2.0
Requires: python-cryptography

Obsoletes: nodeconductor-azure

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires: python-setuptools

%description
Waldur plugin for managing MS Azure resources.

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
* Sat Mar 24 2018 Jenkins <jenkins@opennodecloud.com> - 0.3.5-1.el7
- New upstream release

* Fri Dec 1 2017 Jenkins <jenkins@opennodecloud.com> - 0.3.4-1.el7
- New upstream release

* Wed Nov 29 2017 Jenkins <jenkins@opennodecloud.com> - 0.3.3-1.el7
- New upstream release

* Sun Oct 29 2017 Jenkins <jenkins@opennodecloud.com> - 0.3.2-1.el7
- New upstream release

* Mon Aug 28 2017 Jenkins <jenkins@opennodecloud.com> - 0.3.1-1.el7
- New upstream release

* Sat Aug 26 2017 Jenkins <jenkins@opennodecloud.com> - 0.3.0-1.el7
- New upstream release

* Thu Jun 30 2016 Jenkins <jenkins@opennodecloud.com> - 0.2.0-1.el7
- New upstream release

* Mon Jun 27 2016 Jenkins <jenkins@opennodecloud.com> - 0.1.0-1.el7
- New upstream release

* Mon May 9 2016 Victor Mireyev <victor@opennodecloud.com> - 0.1.0-1.el7
- Initial version of the package

