# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
	
	config.vm.box = "debian/jessie64"

	config.vm.provision "ansible" do |ansible|
		ansible.playbook = "radicalspam.yml"
		ansible.sudo = true
	end

	config.vm.provider "virtualbox" do |vb|
		config.vm.network "private_network", ip: "10.0.0.100"
	end

	# HTTP
	config.vm.network "forwarded_port", guest: 80, host: 1080
	# HTTPS
	config.vm.network "forwarded_port", guest: 443, host: 1443
	# SMTP
	config.vm.network "forwarded_port", guest: 25, host: 1025
  
end