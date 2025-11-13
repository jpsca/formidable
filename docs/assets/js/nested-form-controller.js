/* Adapted from "Stimulus Rails Nested Form"
 * https://www.stimulus-components.com/docs/stimulus-rails-nested-form/
 * Copyright (c) Guillaume Briday.
 * Licensed under the MIT License.
*/
import { Controller } from "./stimulus.js";

const parser = new DOMParser();

export default class NestedForm extends Controller {
  static targets = ["target", "template"]
  static values = {
    wrapperSelector: {type: String, default: ".nested-form-wrapper"},
  }

  newIndex = 0

  add(e) {
    e.preventDefault();

    const i = (new Date()).getTime().toString().slice(4);
    const content = this.templateTarget.innerHTML.replace(/NEW_RECORD/g, i);

    // The form template must have a single root element
    const doc = parser.parseFromString(content, "text/html");
    const wrapper = doc.body.firstElementChild;
    wrapper.setAttribute("data-new", "true");

    // Fix ids so they are unique
    wrapper.querySelectorAll("[id]").forEach(el => {
      el.setAttribute("id", `${el.getAttribute("id")}_${i}`);
    });
    wrapper.querySelectorAll("[for]").forEach(el => {
      el.setAttribute("for", `${el.getAttribute("for")}_${i}`);
    });

    this.targetTarget.appendChild(wrapper);
    const event = new CustomEvent("nested-form:add", { bubbles: !0 });
    this.element.dispatchEvent(event);
  }

  remove(e) {
    e.preventDefault();

    const wrapper = e.target.closest(this.wrapperSelectorValue);
    if (wrapper.dataset.newRecord) {
      wrapper.remove();
    } else {
      wrapper.style.display = "none";
      const input = wrapper.querySelector('input[name*="_destroy"]');
      if (input) input.value = "1";
    }

    const event = new CustomEvent("nested-form:remove", { bubbles: !0 });
    this.element.dispatchEvent(event);
  }
};

Stimulus.register("nested-form", NestedForm);
