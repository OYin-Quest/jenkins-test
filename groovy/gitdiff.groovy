// https://medium.com/rocket-travel/running-advanced-git-commands-in-a-declarative-multibranch-jenkinsfile-e82b075dbc53
// https://gist.github.com/mrhockeymonkey/6b7b815b7bf3732f32ad1c5c913afff5

powershell 'gci env:\\ | ft name,value -autosize'

powershell '& git config --add remote.origin.fetch +refs/heads/master:refs/remotes/origin/master'

powershell '& git fetch --no-tags'

powershell '''
			$diffToMaster = & git diff --name-only origin/master..origin/$env:BRANCH_NAME
			Switch($diffToMaster){
				echo $diffToMaster
			}
			gci env:/PACK_*
'''