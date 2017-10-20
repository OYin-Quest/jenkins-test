timestamps{
	node('tcde-win7'){
		try{
			echo "hello, world"
			stage('Preparation'){
				echo 'creating vm'
			}
			stage('run'){
				echo 'run'
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