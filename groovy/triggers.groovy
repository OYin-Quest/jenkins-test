this.triggersMapping = [
	"master" : [
		"on_commit" : {
			print "Entered trigger -> on_commit (on master)"
		}
	],
	"integration" : [
		"on_commit" : {
			print "Entered trigger -> on_commit (on integration)"
		}
	],
]


this.defaultTriggersMappin = [
	"on_commit" : {
		print "Entered default trigger -> on_commit"
	},
	"on_approval" : { target ->
		print "Entered default trigger -> on_approval"
		print "With argument -> ${target}"
	}
]


def callTriggerOnBranch(trigger, branch){
	return this.callTriggerOnBranchWithArgs(trigger, branch, null)
}


def callTriggerOnBranchWithArgs(trigger, branch, args){
	triggers = this.triggersMapping.getOrDefault(branch, this.defaultTriggersMappin)
	return triggers.getOrDefault(trigger, this.defaultTriggersMappin[trigger]).call(args)
}

return this