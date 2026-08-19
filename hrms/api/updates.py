import json

import frappe
from frappe import _
from frappe.desk.form.utils import add_comment as _add_comment
from frappe.desk.like import toggle_like
from frappe.utils import getdate, now_datetime, pretty_date

from hrms.api import get_current_employee

DOCTYPE = "ESS Post"


@frappe.whitelist()
def create_or_update_post(**data) -> dict:
	if data.get("name"):
		post_doc = frappe.get_doc(DOCTYPE, data.get("name"))
		if post_doc.user != frappe.session.user:
			frappe.throw(_("Not permitted"), frappe.PermissionError)
	else:
		post_doc = frappe.new_doc(DOCTYPE)
		post_doc.user = frappe.session.user
		post_doc.employee = get_current_employee()
		post_doc.post_datetime = now_datetime()

	data.pop("name", None)
	post_doc.update(data)
	post_doc.save(ignore_permissions=True)
	return {"name": post_doc.name}


def _get_post(post_name: str) -> dict:
	post = json.loads(frappe.get_doc(DOCTYPE, post_name).as_json())
	for field in ["owner", "creation", "modified", "modified_by", "docstatus", "idx", "doctype"]:
		post.pop(field, None)

	post["comments_count"] = frappe.db.count(
		"Comment",
		{"reference_doctype": DOCTYPE, "reference_name": post_name, "comment_type": "Comment"},
	)

	liked_by = json.loads(post.get("_liked_by") or "[]")
	post["likes_count"] = len(liked_by)
	post["liked_by_me"] = frappe.session.user in liked_by

	if post.get("post_type") == "Poll":
		post["my_vote"] = frappe.db.get_value(
			"ESS Post Poll Log",
			{"user": frappe.session.user, "parent": post_name},
			"answer",
		)
		post["total_votes"] = len(post.get("ess_post_poll_log") or [])
		post["poll_closed"] = bool(
			post.get("poll_end_date") and getdate(post["poll_end_date"]) < getdate()
		)

	if frappe.session.user != post.get("user"):
		post.pop("ess_post_poll_log", None)

	return post


@frappe.whitelist()
def get_feed(my_post: bool = False, start: int = 0, page_length: int = 10) -> list[dict]:
	filters = {"user": frappe.session.user} if my_post else {"publish": 1}

	posts = frappe.get_all(
		DOCTYPE,
		filters=filters,
		fields=["name"],
		start=start,
		page_length=page_length,
		order_by="post_datetime desc",
	)
	return [_get_post(post.name) for post in posts]


@frappe.whitelist()
def get_post(post_name: str) -> dict:
	return _get_post(post_name)


@frappe.whitelist()
def delete_post(post_id: str) -> None:
	if not frappe.db.exists(DOCTYPE, {"user": frappe.session.user, "name": post_id}):
		frappe.throw(_("Not permitted"), frappe.PermissionError)
	frappe.delete_doc(DOCTYPE, post_id, ignore_permissions=True)


@frappe.whitelist()
def toggle_post_like(post_id: str, like: bool = False) -> dict:
	toggle_like(doctype=DOCTYPE, name=post_id, add="Yes" if like else "No")
	return _get_post(post_id)


@frappe.whitelist()
def submit_poll_vote(post_id: str, answer: str) -> dict:
	post_doc = frappe.get_doc(DOCTYPE, post_id)
	if post_doc.poll_end_date and getdate(post_doc.poll_end_date) < getdate():
		frappe.throw(_("Poll has ended"))

	existing_vote = next(
		(log for log in post_doc.ess_post_poll_log if log.user == frappe.session.user), None
	)
	if existing_vote:
		existing_vote.answer = answer
	else:
		post_doc.append("ess_post_poll_log", {"user": frappe.session.user, "answer": answer})

	post_doc.save(ignore_permissions=True)

	return _get_post(post_id)


@frappe.whitelist()
def add_comment(post_id: str, content: str) -> None:
	comment_by = frappe.db.get_value("User", frappe.session.user, "full_name")
	_add_comment(
		reference_doctype=DOCTYPE,
		reference_name=post_id,
		content=content,
		comment_email=frappe.session.user,
		comment_by=comment_by,
	)


@frappe.whitelist()
def get_comments(post_id: str, start: int = 0, page_length: int = 20) -> list[dict]:
	comments = frappe.get_all(
		"Comment",
		filters={
			"reference_doctype": DOCTYPE,
			"reference_name": post_id,
			"comment_type": "Comment",
		},
		fields=["content", "comment_by", "comment_email", "creation"],
		start=start,
		page_length=page_length,
		order_by="creation desc",
	)
	for comment in comments:
		comment["user_image"] = frappe.get_cached_value("User", comment.comment_email, "user_image")
		comment["commented"] = pretty_date(comment["creation"])
	return comments
