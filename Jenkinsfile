
properties([
	buildDiscarder(
		logRotator(
			artifactDaysToKeepStr: '', 
			artifactNumToKeepStr: '', 
			daysToKeepStr: '7', 
			numToKeepStr: '15'
		)
	), 
	parameters([
		string(
			defaultValue: 'automation', 
			description: 'Branch where test code was fetched from.', 
			name: 'TEST_BRANCH'
		),
		string(
			defaultValue: 'master', 
			description: 'Branch where installer was built from.', 
			name: 'INSTALLER_BRANCH'
		),
		string(
			defaultValue: '', 
			description: 'Use specific installer name instead of getting latest one by INSTALLERR_BRANCH.', 
			name: 'INSTALLER_NAME'
		),
		string(
			defaultValue: '4.5', 
			description: '', 
			name: 'INSTALLER_VERSION'
		),
		string(
			defaultValue: 'smoke', 
			description: '', 
			name: 'TEST_TYPE'
		),
		string(
			defaultValue: 'Chrome', 
			description: 'Supported value: IE, Chrome, Firefox', 
			name: 'BROWSER_TYPE'
		),
		[
			$class: 'LabelParameterDefinition',
			allNodesMatchingLabel: false,
			defaultValue: 'auto7',
			description: '',
			name: 'label',
			nodeEligibility: [$class: 'AllNodeEligibility'],
			triggerIfResult: 'allCases'
		]
	])
])

timestamps{
	withWorkspace('auto7', 'TCDE'){	
		try{
			env.PROPERTY_APIKEY = '-H "X-JFrog-Art-Api:AKCp2WY1Kb9Xs68829rBntbPZg6oKe4vA4JvXSAp4WDn3FGCaaT4bChMxgpHBzQCUqmomp7yD"'
			
			// Using the 'stage' step without a block argument is deprecated.
			stage('CheckOut Source Code'){
				// Copy SSH keys for git clone.
				bat "mkdir C:\\Tools\\QSFTSSH > nul || echo bypass error"
				bat "curl ${env.PROPERTY_APIKEY} https://artifactory.labs.quest.com/toad-intelligence-central/Components/QSFT/id_rsa -o C:\\Tools\\QSFTSSH\\id_rsa > nul"
				bat "curl ${env.PROPERTY_APIKEY} https://artifactory.labs.quest.com/toad-intelligence-central/Components/QSFT/id_rsa.pub -o C:\\Tools\\QSFTSSH\\id_rsa.pub > nul"
				bat "curl ${env.PROPERTY_APIKEY} https://artifactory.labs.quest.com/toad-intelligence-central/Components/QSFT/known_hosts -o C:\\Tools\\QSFTSSH\\known_hosts > nul"
			
				bat "xcopy C:\\Tools\\QSFTSSH ${env.USERPROFILE}\\.ssh /I /Y > nul"
				bat "RD /S /Q . > nul || echo bypass error"
				def testRepo = 'TCDE'
				def testBranch = getTestBranch(testRepo, env.TEST_BRANCH)
				checkoutBranch(testRepo, testBranch)
			}
			
			stage('Run Tests'){			
				bat "ant -file \"test\\Jenkins Build Scripts\\Automation.xml\" -DINSTALLER_BRANCH=${env.INSTALLER_BRANCH} \"-DINSTALLER_NAME=${env.INSTALLER_NAME}\" -DTEST_BRANCH=${env.TEST_BRANCH} -DINSTALLER_VERSION=${env.INSTALLER_VERSION}  -DTEST_TYPE=${env.TEST_TYPE} -DBROWSER_TYPE=${env.BROWSER_TYPE} -DSiteCode=azure \"-DProductName=TICBundle${env.INSTALLER_VERSION},TICAC4.3\" Preparation"
				
				setBuildName()
				
				bat "ant -file \"test\\Jenkins Build Scripts\\Automation.xml\" -DINSTALLER_BRANCH=${env.INSTALLER_BRANCH} \"-DINSTALLER_NAME=${env.INSTALLER_NAME}\" -DTEST_BRANCH=${env.TEST_BRANCH} -DINSTALLER_VERSION=${env.INSTALLER_VERSION}  -DTEST_TYPE=${env.TEST_TYPE} -DBROWSER_TYPE=${env.BROWSER_TYPE} -DSiteCode=azure \"-DProductName=TICBundle${env.INSTALLER_VERSION},TICAC4.3\" RunTestInPython"
				
				bat 'type C:\\AutomationLog\\tic_pythontest.log'
				
				// Copy test results to workspace
				bat "XCOPY C:\\Automation\\TestResults \"${env.WORKSPACE}\\TestResults\" /S /I /Y > nul"
			}
			currentBuild.result = "SUCCESS"
		} catch(error){
			currentBuild.result = "FAILURE"
			throw error
		} finally{
			archiveArtifacts allowEmptyArchive: true, artifacts: 'env.txt,test.properties,TestResults/Support_Bundle/*.*'
			try{
				// Below two publish reports would throw error and mark build failed.
				publishHTMLReport()
				publishJUnitReport()
			} catch(postError){
				currentBuild.result = "FAILURE"
				throw postError
			} finally{
				// Close slave VM in the end.
				notifySlack()
				closeSlaveVM()
			}
		}
	}
}

void withWorkspace(def label, def space, def body){
	node(label){
		ws(space){
			body.call()
		}
	}
}

def getTestBranch(def repo, def branch){
	if (isBranchExist(repo, branch)){
		return branch
	}
	def automationBranch = "automation"
	if (isBranchExist(repo, automationBranch)){
		return automationBranch
	}
}

def isBranchExist(def repo, def branch){
	def cmdStatus = bat(script:"git ls-remote --heads git@github.com:QSFT/${repo}.git ${branch} | findstr ${branch}", returnStatus: true)
	return cmdStatus ==0
}

def checkoutBranch(def repo, def branch){
	echo "Checkout branch: ${branch} from repository: ${repo}"
	bat 'git config --global user.email "intersect.build@quest.com"'
	bat 'git config --global user.name "Intersect Builder"'
	git branch: "${branch}", credentialsId: 'github-tic', url: "git@github.com:QSFT/${repo}.git"
}

def setBuildName(){
	def buildName = readFile 'version.txt'
	currentBuild.displayName = buildName
}

def notifySlack(){
    def color = 'good'
    if (currentBuild.result == "SUCCESS"){
        color = "good"
    } else if (currentBuild.result == "FAILURE"){
        color = "danger"
    } else {
        color = "warning"
    }
    slackSend channel: '#tic-ci', color: "${color}", message: "Jenkins build is ${currentBuild.result}: ${currentBuild.rawBuild.project.fullDisplayName} #${env.BUILD_NUMBER} (<${env.RUN_DISPLAY_URL}|Open>)", tokenCredentialId: 'SLACK_JENKINS_TIC_TOKEN'
}

def publishHTMLReport(){
	publishHTML([
				allowMissing: false, 
				alwaysLinkToLastBuild: false, 
				keepAll: true, 
				reportDir: 'TestResults/Support_Bundle/webhtml', 
				reportFiles: 'webtest.html', 
				reportName: 'HTML Report', 
				reportTitles: ''
				])
}

def publishJUnitReport(){
	junit 'TestResults/Support_Bundle/weblog/web_junit_result.xml'
}

def closeSlaveVM(){
	// add test code branch info
	manager.addShortText(env.TEST_BRANCH)

	// delete slave node
	for (slave in hudson.model.Hudson.instance.slaves) {
		if (slave.name == env.NODE_NAME) {
			echo "Delete slave node ${slave.name}"
			slave.getComputer().doDoDisconnect("Job finished.")
			slave.getComputer().doDoDelete()
		}
	}
}