# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import add_days, cint, today


class ESSPost(Document):
	def validate(self):
		if self.post_type == "Poll":
			self.poll_start_date = today()
			self.poll_end_date = add_days(today(), cint(self.poll_duration))
		if not self.get("__islocal"):
			answer_map_dict = self.get_answer_map()
			for op in self.ess_post_poll_options:
				option_answers = answer_map_dict.get(op.get("option"))
				if option_answers:
					op.num_of_vote = len(option_answers)
					op.percentage = 100 * op.num_of_vote / len(self.ess_post_poll_log)
				else:
					op.num_of_vote = 0
					op.percentage = 0
			# flips on every save so that realtime doctype subscribers
			# (poll vote counts) always see a fresh `modified` revision
			self.update_post = not self.update_post

	def get_answer_map(self):
		answers = {}
		for poll_ans in self.ess_post_poll_log:
			if not answers.get(poll_ans.get("answer")):
				answers[poll_ans.get("answer")] = [poll_ans]
			else:
				answers[poll_ans.get("answer")].append(poll_ans)
		return answers
