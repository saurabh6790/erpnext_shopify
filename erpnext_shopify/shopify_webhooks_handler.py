import frappe
from frappe import _
from .exceptions import ShopifyError
from .utils import create_log_entry



def shopify_webhook(f):
	"""
	A decorator thats checks and validates a Shopify Webhook request.
	"""

	def _hmac_is_valid(body, secret, hmac_to_verify):
		secret = str(secret)
		hash = hmac.new(secret, body, hashlib.sha256)
		hmac_calculated = base64.b64encode(hash.digest())
		return hmac_calculated == hmac_to_verify

	@wraps(f)
	def wrapper(*args, **kwargs):
		# Try to get required headers and decode the body of the request.
		try:
			webhook_topic = frappe.local.request.headers.get('X-Shopify-Topic')
			webhook_hmac	= frappe.local.request.headers.get('X-Shopify-Hmac-Sha256')
			webhook_data	= frappe._dict(json.loads(frappe.local.request.get_data()))
		except:
			raise ValidationError()

		# Verify the HMAC.
		if get_shopify_settings().password:
			if not _hmac_is_valid(frappe.local.request.get_data(), get_shopify_settings().password, webhook_hmac):
				raise AuthenticationError()

			# Otherwise, set properties on the request object and return.
		frappe.local.request.webhook_topic = webhook_topic
		frappe.local.request.webhook_data  = webhook_data
		kwargs.pop('cmd')

		return f(*args, **kwargs)
	return wrapper


@frappe.whitelist(allow_guest=True)
@shopify_webhook
def webhook_handler():
	from webhooks import handler_map
	topic = frappe.local.request.webhook_topic
	data = frappe.local.request.webhook_data
	
	webhook_handler = frappe.new_doc("Webhook Request Handler")
	webhook_handler.event = topic
	webhook_handler.request_data = json.dumps(data)
	webhook_handler.save(ignore_permissions=True)
	
	# handler = handler_map.get(topic)
# 	if handler:
# 		handler(data)
