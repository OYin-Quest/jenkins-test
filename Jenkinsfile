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
			stage('cleanup'){
				echo 'cleanup'
			}
			stage('copy'){
				echo 'copy artifacts'
			}
		}
	}
}