#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_with	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
Summary:	Atheros WiFi card driver
Summary(pl):	Sterownik karty radiowej Atheros
Name:		madwifi
Version:	0
%define		snap	20050119
%define		snapdate	2005-01-19
%define		_rel	0.%{snap}.1
Release:	%{_rel}
Epoch:		0
License:	GPL
Group:		Base/Kernel
Source0:	http://madwifi.otaku42.de/2005/01/madwifi-cvs-snapshot-%{snapdate}.tar.bz2
# Source0-md5:	2337699afaa8e3c552097db934ba408e
URL:		http://madwifi.sf.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.153
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Atheros WiFi card driver

%description -l pl
Sterownik karty radiowej Atheros

# kernel subpackages.

%package -n kernel-net-atheros
Summary:	Linux driver for Atheros cards
Summary(pl):	Sterownik dla Linuksa do kart Atheros
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-net-atheros
This is driver for Atheros card for Linux.

This package contains Linux module.

%description -n kernel-net-atheros -l pl
Sterownik dla Linuksa do kart Atheros.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel-smp-net-atheros
Summary:	Linux SMP driver for %{name} cards
Summary(pl):	Sterownik dla Linuksa SMP do kart %{name}
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-net-atheros
This is driver for Atheros cards for Linux.

This package contains Linux SMP module.

%description -n kernel-smp-net-atheros -l pl
Sterownik dla Linuksa do kart Atheros.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q -n %{name}

%build
%if %{with userspace}


%endif

%if %{with kernel}
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include/{linux,config,asm}
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	touch include/config/MARKER
#
#	patching/creating makefile(s) (optional)
#
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} \
		O=$PWD \
		CC="%{__cc}" CPP="%{__cpp}" \
		%{?with_verbose:V=1}

	mv ath/ath_pci{,-$cfg}.ko
	mv ath_hal/ath_hal{,-$cfg}.ko
	mv ath_rate/onoe/ath_rate_onoe{,-$cfg}.ko
	for i in wlan_wep wlan_xauth wlan_acl wlan_ccmp wlan_tkip wlan; do
		mv net80211/$i{,-$cfg}.ko
	done
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}


%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/net
install ath/ath_pci-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/net/ath_pci.ko
install ath_hal/ath_hal-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/net/ath_hal.ko
install ath_rate/onoe/ath_rate_onoe-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/net/ath_rate_onoe.ko
for i in wlan_wep wlan_xauth wlan_acl wlan_ccmp wlan_tkip wlan; do
	install net80211/$i-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/net/$i.ko
done
%if %{with smp} && %{with dist_kernel}
install ath/ath_pci-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/net/ath_pci.ko
install ath_hal/ath_hal-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/net/ath_hal.ko
install ath_rate/onoe/ath_rate_onoe-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/net/ath_rate_onoe.ko
for i in wlan_wep wlan_xauth wlan_acl wlan_ccmp wlan_tkip wlan; do
	install net80211/$i-smp.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/net/$i.ko
done
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-net-atheros
%depmod %{_kernel_ver}

%postun	-n kernel-net-atheros
%depmod %{_kernel_ver}

%post	-n kernel-smp-net-atheros
%depmod %{_kernel_ver}smp

%postun	-n kernel-smp-net-atheros
%depmod %{_kernel_ver}smp

%if %{with kernel}
%files -n kernel-net-atheros
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/net/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-atheros
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/net/*.ko*
%endif
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)

%endif
