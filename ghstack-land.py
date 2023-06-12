#!/usr/bin/env python3

import argparse
import os

import ghstack.shell
import ghstack.github_real
import ghstack.land
import ghstack.logs


def land(pr_url):
    with ghstack.logs.manager(debug=False):
        sh = ghstack.shell.Shell()
        github = ghstack.github_real.RealGitHubEndpoint(
            oauth_token=os.environ['GITHUB_TOKEN'],
            github_url='github.com',
        )
        ghstack.land.main(
            pull_request=pr_url,
            github=github,
            sh=sh,
            github_url='github.com',
            remote_name='origin',
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pull_request', type=str, help='URL of pull request to land')
    options = parser.parse_args()

    land(options.pull_request)


if __name__ == "__main__":
    main()
