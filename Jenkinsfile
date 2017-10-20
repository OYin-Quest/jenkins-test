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
			stage('cleanup'){
				echo 'cleanup'
			}
			stage('copy'){
				echo 'copy artifacts'
			}
		} catch(error){
			echo "catch"
			throw error
		} finally{
			echo "finally"
		}
	}
}