import frappe
from frappe import _
from frappe.utils import get_url
from functools import wraps
import hashlib, base64, hmac, json
from .shopify_requests import get_request, post_request, get_shopify_settings
from .exceptions import ShopifyWebhookSetupError

def create_webhooks():
	settings = get_shopify_settings()
	if not settings.is_webhook_created:
		for event in ["customers/enable", "customers/disable", "customers/delete", "products/delete"]:
			create_webhook(event)
		frappe.db.set_value("Shopify Settings", None, "is_webhook_created", 1)

def create_webhook(topic):
	try:
		post_request('admin/webhooks.json', json.dumps({
			"webhook": {
				"topic": topic,
				"address": get_url("/api/method/erpnext_shopify.shopify_webhooks_handler.webhook_handler"),
				"format": "json"
			}
		}))
	except ShopifyWebhookSetupError, e:
		raise e

def get_webhooks():
	webhooks = get_request("/admin/webhooks.json")
	return webhooks["webhooks"]

def delete_webhooks():
	webhooks = get_webhooks()
	for webhook in webhooks:
		delete_request("/admin/webhooks/{}.json".format(webhook['id']))
