/* Adapted from "Stimulus Rails Nested Form"
 * https://www.stimulus-components.com/docs/stimulus-rails-nested-form/
 * Copyright (c) Guillaume Briday.
 * Licensed under the MIT License.
*/
import { Controller } from "./stimulus.js";

export default class NestedForm extends Controller {
  static targets = ["target", "template"]
  static values = {
    wrapperSelector: {
      type: String,
      default: ".nested-form-wrapper",
    },
  }

  newIndex = 0

  add(e) {
    e.preventDefault();
    const content = this.templateTarget.innerHTML.replace(/NEW_RECORD/g, (new Date()).getTime().toString());
    this.targetTarget.insertAdjacentHTML("beforeend", content);
    const event = new CustomEvent("nested-form:add", { bubbles: !0 });
    this.element.dispatchEvent(event);
  }

  remove(e) {
    e.preventDefault();
    const wrapper = e.target.closest(this.wrapperSelectorValue);
    if (wrapper.dataset.newRecord)
      wrapper.remove();
    else {
      wrapper.style.display = "none";
      const input = wrapper.querySelector("input[name*='_destroy']");
      input.value = "1";
    }
    const event = new CustomEvent("nested-form:remove", { bubbles: !0 });
    this.element.dispatchEvent(event);
  }
};

Stimulus.register("nested-form", NestedForm);
