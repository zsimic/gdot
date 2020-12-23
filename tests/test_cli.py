def test_sanity_check(cli):
    cli.expect_success("--help")
    cli.expect_success("--version")
