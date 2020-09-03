this.tdpMapping = [
	"pipeline-testA" : [
		"branchName" : {
			return "tdp_branchA"
		}
	],
]


this.defaultTdpMapping = [
	"branchName" : {
		return 'master'
	},
	"version" : { 
		return '5.2.1'
	}
]


def callMappingOnBranch(trigger, branch){
	return this.callTriggerOnBranchWithArgs(trigger, branch, null)
}


def callMappingOnBranchWithArgs(trigger, branch, args){
	triggers = this.tdpMapping.getOrDefault(branch, this.defaultTriggersMappin)
	return triggers.getOrDefault(trigger, this.defaultTdpMapping[trigger]).call(args)
}

return this