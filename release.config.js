module.exports = {
	branches: ["main", {"name": "dev", "prerelease": true}],
	repositoryUrl: "https://github.com/devops-dislinkt/user-profile",
	plugins: [
		"@semantic-release/commit-analyzer",
		"@semantic-release/release-notes-generator",
		["@semantic-release/github", {
			assets: [
				{"path": "dist/*.gz", "label": "CSS distribution"},
				{"path": "coverage.xml", "label": "Code coverage"}
			]
		}
	]
}