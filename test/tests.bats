load 'test_helper/bats-support/load'
load 'test_helper/bats-assert/load'

@test "checking configuration: hostname/domainname" {
  run docker run `docker inspect --format '{{ .Config.Image }}' mail`
  assert_failure
}

@test "checking configuration: hostname/domainname override" {
  run docker exec mail /bin/bash -c "cat /etc/mailname | grep my-domain.com"
  assert_success
}