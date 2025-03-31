/**
 * DOMSimplifier - Traverses the DOM and creates a simplified representation
 * for browser automation and web scraping purposes
 */
class DOMSimplifier {
	constructor() {
		this.simplifiedDOM = {
			nodeType: "root",
			children: [],
		};
	}

	/**
	 * Process the entire document and return a simplified DOM structure
	 * @returns {Object} Simplified DOM structure
	 */
	simplifyDocument() {
		// Start from document body
		if (document && document.body) {
			this.processNode(document.body, this.simplifiedDOM);
		} else {
			console.warn("Document body is not available");
		}
		return this.simplifiedDOM;
	}

	/**
	 * Recursively process a DOM node and its children
	 * @param {Node} node - DOM node to process
	 * @param {Object} parentSimplified - Parent node in the simplified structure
	 */
	processNode(node, parentSimplified) {
		// Check if node is null or undefined
		if (!node) {
			return;
		}

		// Skip invisible or irrelevant elements
		if (this.shouldSkipNode(node)) {
			return;
		}

		// Create simplified representation of the current node
		const simplifiedNode = this.createSimplifiedNode(node);

		if (simplifiedNode) {
			// Add to parent's children
			parentSimplified.children.push(simplifiedNode);

			// Process child nodes recursively
			if (node.childNodes && node.childNodes.length > 0) {
				// Add children array to simplified node
				simplifiedNode.children = [];

				for (let i = 0; i < node.childNodes.length; i++) {
					this.processNode(node.childNodes[i], simplifiedNode);
				}
			}
		}
	}

	/**
	 * Safely get string value from an attribute that might not be a string
	 * @param {*} value - The attribute value
	 * @returns {string} String representation of the value
	 */
	safeString(value) {
		if (value === null || value === undefined) {
			return "";
		}

		// Handle DOMTokenList (like classList)
		if (value instanceof DOMTokenList) {
			return Array.from(value).join(" ");
		}

		// Handle SVGAnimatedString or other objects with baseVal
		if (value && typeof value === "object" && "baseVal" in value) {
			return value.baseVal;
		}

		return String(value);
	}

	/**
	 * Determine if a node should be skipped (ads, trackers, invisible elements)
	 * @param {Node} node - DOM node to check
	 * @returns {boolean} True if node should be skipped
	 */
	shouldSkipNode(node) {
		// Check if node is null or undefined
		if (!node) {
			return true;
		}

		// Skip comment nodes and other non-element nodes
		if (
			node.nodeType !== Node.ELEMENT_NODE &&
			node.nodeType !== Node.TEXT_NODE
		) {
			return true;
		}

		if (node.nodeType === Node.ELEMENT_NODE) {
			const element = node;

			try {
				const style = window.getComputedStyle(element);

				// Skip invisible elements
				if (
					style.display === "none" ||
					style.visibility === "hidden" ||
					style.opacity === "0"
				) {
					return true;
				}
			} catch (e) {
				// If we can't get computed style, don't skip the element
			}

			// Skip common ad and tracking elements
			const tagName = element.tagName.toLowerCase();
			const id = element.id
				? this.safeString(element.id).toLowerCase()
				: "";
			const className = this.safeString(element.className).toLowerCase();

			// Check for common ad, cookie, tracker elements
			const adKeywords = [
				"ad",
				"ads",
				"advertisement",
				"banner",
				"promotion",
				"sponsor",
			];
			const cookieKeywords = [
				"cookie",
				"consent",
				"gdpr",
				"privacy-alert",
			];
			const skipWords = [
				...adKeywords,
				...cookieKeywords,
				"analytics",
				"tracker",
				"tracking",
			];

			// Check if element matches ad patterns
			const matchesSkipPattern = skipWords.some(
				(word) =>
					id.includes(word) ||
					className.includes(word) ||
					(element.getAttribute("aria-label") &&
						this.safeString(element.getAttribute("aria-label"))
							.toLowerCase()
							.includes(word))
			);

			// Skip common ad iframes and elements
			if (
				(tagName === "iframe" && matchesSkipPattern) ||
				(tagName === "div" && matchesSkipPattern)
			) {
				return true;
			}
		}

		return false;
	}

	/**
	 * Create a simplified representation of a DOM node
	 * @param {Node} node - DOM node to simplify
	 * @returns {Object|null} Simplified node object or null if not relevant
	 */
	createSimplifiedNode(node) {
		// Check if node is null or undefined
		if (!node) {
			return null;
		}

		// Handle text nodes
		if (node.nodeType === Node.TEXT_NODE) {
			const text = node.textContent.trim();
			// Only include non-empty text nodes
			if (text) {
				return {
					nodeType: "text",
					content: text,
				};
			}
			return null;
		}

		// Handle element nodes
		if (node.nodeType === Node.ELEMENT_NODE) {
			const element = node;
			const tagName = element.tagName.toLowerCase();

			// Create basic node structure
			const simplified = {
				nodeType: "element",
				tagName: tagName,
			};

			// Collect attributes that are useful for identification and interaction
			const attributes = {};

			// Store important attributes
			const importantAttrs = [
				"id",
				"class",
				"name",
				"value",
				"href",
				"src",
				"alt",
				"title",
				"aria-label",
				"aria-labelledby",
				"aria-describedby",
				"role",
				"placeholder",
				"type",
				"data-testid",
				"for",
				"action",
				"method",
			];

			importantAttrs.forEach((attr) => {
				if (element.hasAttribute(attr)) {
					attributes[attr] = element.getAttribute(attr);
				}
			});

			// Include attributes if not empty
			if (Object.keys(attributes).length > 0) {
				simplified.attributes = attributes;
			}

			// For input elements, include checked state if relevant
			if (
				tagName === "input" &&
				(element.type === "checkbox" || element.type === "radio")
			) {
				simplified.checked = element.checked;
			}

			// For select elements, include selected options
			if (tagName === "select" && element.options.length > 0) {
				simplified.selectedIndex = element.selectedIndex;
				if (element.selectedIndex >= 0) {
					simplified.selectedValue =
						element.options[element.selectedIndex].value;
					simplified.selectedText =
						element.options[element.selectedIndex].text;
				}
			}

			// Store text content for elements that typically have direct text
			if (
				[
					"button",
					"a",
					"h1",
					"h2",
					"h3",
					"h4",
					"h5",
					"h6",
					"label",
					"li",
					"span",
					"p",
					"div",
					"td",
					"th",
				].includes(tagName)
			) {
				const directText = Array.from(element.childNodes)
					.filter((child) => child.nodeType === Node.TEXT_NODE)
					.map((child) => child.textContent.trim())
					.join(" ")
					.trim();

				if (directText) {
					simplified.textContent = directText;
				}
			}

			// Determine if element is interactive
			if (
				tagName === "a" ||
				tagName === "button" ||
				tagName === "input" ||
				tagName === "select" ||
				tagName === "textarea" ||
				tagName === "label" ||
				element.hasAttribute("onclick") ||
				element.hasAttribute("onsubmit") ||
				element.getAttribute("role") === "button" ||
				element.getAttribute("role") === "link" ||
				element.getAttribute("tabindex") === "0"
			) {
				simplified.interactive = true;
			}

			return simplified;
		}

		return null;
	}

	/**
	 * Convert simplified DOM structure to HTML string
	 * @param {Object} node - Node in the simplified structure
	 * @param {number} depth - Current depth in the tree (for indentation)
	 * @returns {string} HTML representation of the simplified DOM
	 */
	toHTML(node = this.simplifiedDOM, depth = 0) {
		if (!node) return "";

		const indent = "  ".repeat(depth);
		let html = "";

		if (node.nodeType === "root") {
			html = '<div class="simplified-dom-root">\n';
			if (node.children && node.children.length) {
				node.children.forEach((child) => {
					html += this.toHTML(child, depth + 1);
				});
			}
			html += "</div>\n";
		} else if (node.nodeType === "text") {
			html = `${indent}${node.content}\n`;
		} else if (node.nodeType === "element") {
			const attrs = node.attributes || {};
			let attrsStr = "";

			// Format attributes
			Object.keys(attrs).forEach((key) => {
				attrsStr += ` ${key}="${attrs[key]}"`;
			});

			// Add interactive indicator if applicable
			if (node.interactive) {
				attrsStr += ' data-interactive="true"';
			}

			// Handle self-closing tags
			const selfClosingTags = [
				"img",
				"input",
				"br",
				"hr",
				"meta",
				"link",
			];
			if (
				selfClosingTags.includes(node.tagName) &&
				(!node.children || node.children.length === 0)
			) {
				html = `${indent}<${node.tagName}${attrsStr} />\n`;
			} else {
				// Opening tag
				html = `${indent}<${node.tagName}${attrsStr}>`;

				// Add text content if available
				if (node.textContent) {
					html += `${node.textContent}`;
				}

				// Add children if available
				if (node.children && node.children.length) {
					html += "\n";
					node.children.forEach((child) => {
						html += this.toHTML(child, depth + 1);
					});
					html += indent;
				}

				// Closing tag
				html += `</${node.tagName}>\n`;
			}
		}

		return html;
	}

	/**
	 * Create a selector string for identifying an element
	 * @param {Object} simplifiedNode - Simplified node to create selector for
	 * @returns {string} CSS or XPath selector for the element
	 */
	createSelector(simplifiedNode) {
		if (!simplifiedNode || simplifiedNode.nodeType !== "element") {
			return null;
		}

		const attrs = simplifiedNode.attributes || {};

		// Try to create CSS selector
		if (attrs.id) {
			return `#${attrs.id}`;
		}

		// Use tag and class
		if (attrs.class) {
			const classes = attrs.class
				.split(/\s+/)
				.map((c) => `.${c}`)
				.join("");
			return `${simplifiedNode.tagName}${classes}`;
		}

		// Use name attribute if available (common for form elements)
		if (attrs.name) {
			return `${simplifiedNode.tagName}[name="${attrs.name}"]`;
		}

		// Use other significant attributes
		if (attrs["data-testid"]) {
			return `[data-testid="${attrs["data-testid"]}"]`;
		}

		if (attrs["aria-label"]) {
			return `${simplifiedNode.tagName}[aria-label="${attrs["aria-label"]}"]`;
		}

		// If it has text content, use that
		if (simplifiedNode.textContent) {
			const text = simplifiedNode.textContent
				.substring(0, 20)
				.replace(/"/g, '\\"');
			return `//${simplifiedNode.tagName}[contains(text(), "${text}")]`;
		}

		// If all else fails, return the tag name
		return simplifiedNode.tagName;
	}
}

// Function to run the simplifier from a browser or injected script
function simplifyDOM() {
	const simplifier = new DOMSimplifier();
	const simplifiedDOM = simplifier.simplifyDocument();
	const html = simplifier.toHTML();

	// Return both the structured object and HTML representation
	return {
		structure: simplifiedDOM,
		html: html,
	};
}

// Export for use in Node.js via libraries like Playwright or Puppeteer
// This is compatible with running in a browser context when injected
if (typeof module !== "undefined" && module.exports) {
	module.exports = { DOMSimplifier, simplifyDOM };
}
