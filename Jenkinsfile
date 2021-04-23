timestamps{
	node{
		try{
			echo "hello, world"
			stage('Preparation'){
				echo 'creating vm'
			}
			stage('run'){
				echo 'run'
			}
			
			stage('deploy'){
				echo 'deploy'
			}
		} catch(error){
			echo "catch"
			throw error
		} finally{
			echo "finally"
			stage('copy'){
				echo 'copy artifacts'
			}
			stage('cleanup'){
				echo 'cleanup'
			}
		}
	}
}