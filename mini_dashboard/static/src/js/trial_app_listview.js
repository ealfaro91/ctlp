/** @odoo-module **/
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { TrialAppDashBoard } from '@trial_mini_dashboard/js/trial_app_dashboard';

/**
 * Trial dashboard Renderer class for list view, extending the base ListRenderer.
 * @extends ListRenderer
 */
export class TrialAppDashBoardRenderer extends ListRenderer {};

// Template for the TrialAppDashBoardRenderer component
TrialAppDashBoardRenderer.template = 'trial_mini_dashboard.TrialAppListView';

// Components used by TrialAppDashBoardRenderer
TrialAppDashBoardRenderer.components = Object.assign({}, ListRenderer.components, { TrialAppDashBoard });

/**
 * Trial Dashboard List View configuration.
 * @type {Object}
 */
export const TrialAppDashBoardListView = {
    ...listView,
    // Use the custom TrialAppDashBoardRenderer as the renderer for the list view
    Renderer: TrialAppDashBoardRenderer,
};

// Register the Trial Dashboard List View in the "views" category of the registry
registry.category("views").add("trial_appointment_dashboard_list", TrialAppDashBoardListView);
