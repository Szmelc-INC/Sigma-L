from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import json
import re
import base64


def generate_key_pair():
    """Generate RSA key pair."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


def serialize_key(key, private=False):
    """Serialize the public or private key to send over the network."""
    if private:
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    else:
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )


def deserialize_key(key_data):
    """Deserialize a public key received over the network."""
    return serialization.load_pem_public_key(key_data)


def is_url(text):
    """Check if the given text is a URL."""
    url_regex = re.compile(
        r'(https?://\S+|www\.\S+)',
        re.IGNORECASE
    )
    return re.match(url_regex, text) is not None


def split_message(message):
    """Split the message into URLs and non-URLs while preserving spaces."""
    parts = re.split(r'(\s+)', message)
    encrypted_parts = []
    non_encrypted_parts = []
    
    for part in parts:
        if is_url(part):
            non_encrypted_parts.append(part)
        else:
            encrypted_parts.append(part)

    return encrypted_parts, non_encrypted_parts


def encrypt_message(message, public_key):
    """Encrypt a message using the remote's public key, skipping URLs."""
    encrypted_parts, non_encrypted_parts = split_message(message)
    encrypted_message = []

    for part in encrypted_parts:
        if part.strip() != '':  # Encrypt non-space parts only
            encrypted = public_key.encrypt(
                part.encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            encrypted_message.append(base64.b64encode(encrypted).decode('utf-8'))
        else:
            # Preserve spaces in the encrypted message list
            encrypted_message.append(' ')  

    # Use JSON to structure the message
    return json.dumps({
        'encrypted': encrypted_message,
        'plaintext': non_encrypted_parts
    })


def decrypt_message(encrypted_message, private_key):
    """Decrypt a message using the private key, keeping URLs intact."""
    try:
        # Parse the JSON structure
        message_structure = json.loads(encrypted_message)
        encrypted_parts = message_structure['encrypted']
        non_encrypted_parts = message_structure['plaintext']

        decrypted_message = []

        for encrypted_part in encrypted_parts:
            if encrypted_part == ' ':
                decrypted_message.append(' ')  # Add space back
            else:
                decrypted = private_key.decrypt(
                    base64.b64decode(encrypted_part),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                )
                decrypted_message.append(decrypted.decode('utf-8'))

        # Combine decrypted parts and keep plaintext URLs intact
        combined_message = ''.join(decrypted_message)
        formatted_plaintext = ''.join(non_encrypted_parts)
        
        return combined_message + formatted_plaintext

    except Exception as e:
        return f"Decryption error: {e}"


def make_urls_clickable(text):
    url_regex = r'(https?://\S+)'
    # Display as <URL> but make it clickable by wrapping with <a> tag
    return re.sub(url_regex, r'<a href="\1" title="\1">&lt;URL&gt;</a>', text)


def load_config():
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        print("Config file not found. Using default settings.")
        return None
    except json.JSONDecodeError:
        print("Error decoding config file. Using default settings.")
        return None
