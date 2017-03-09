Vagrant.configure(2) do |config|

  	config.vm.provider "virtualbox" do |v|
    	v.memory = 2048
    	v.cpus = 2
	end
	
	config.vm.box = "ubuntu/xenial64"

	config.vm.provision "ansible" do |ansible|
		ansible.playbook = "radicalspam.yml"
		ansible.sudo = true
	end

	config.vm.provider "virtualbox" do |vb|
		config.vm.network "private_network", ip: "10.0.0.100"
	end

	# SMTP
	config.vm.network "forwarded_port", guest: 25, host: 25

	# SMTP TLS
	config.vm.network "forwarded_port", guest: 465, host: 465
  
end