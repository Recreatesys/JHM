/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

class EventDashboard extends Component {
    setup() {
        this.orm = useService("orm")
        this.action = useService("action")
        this.state = useState({
            eventStats: [],
        });

        onWillStart(async () => {
            const stageEndedId = await this.getEndedStageId();
            await this.fetchEventData(stageEndedId);
        });

    }
    async getEndedStageId() {
        const stages = await this.orm.searchRead("event.stage", [["name", "ilike", "ended"]], ["id"]);
        return stages.length ? stages[0].id : false;
    }

    async fetchEventData(stageEndedId) {
        if (!stageEndedId) return;

        const events = await this.orm.searchRead("event.event", [["stage_id", "=", stageEndedId]], ["name"], { order: "id desc" });
        const result = [];

        for (const event of events) {
            const event_id = event.id;

            const registrantsCount = await this.orm.searchCount("event.registration",[
            ["event_id", "=", event_id],["state","=", "open"],
            ]);

            const attendeesCount = await this.orm.searchCount("event.registration",[
            ["event_id", "=", event_id],["state","=", "done"],
            ]);

            const totalRegistrantsCount = await this.orm.searchCount("event.registration",[
            ["event_id", "=", event_id]
            ]);

            const attendancePercent =
                registrantsCount > 0
                ? Math.round((attendeesCount / totalRegistrantsCount) * 100)
                : 0;

            result.push({
                id: event.id,
                name: event.name,
                registrants: registrantsCount,
                attendees: attendeesCount,
                percent: attendancePercent,
            });
        }
        this.state.eventStats = result;
    }

    openRegistrantlist(event_id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Registrants List",
            res_model: "event.registration",
            domain: [["event_id", "=", event_id],["state","=", "open"]],
            views: [
                    [false, 'list']
            ],
            target: "current",
        });
    }

    openAttendeeslist(event_id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Attendees List",
            res_model: "event.registration",
            domain: [["event_id", "=", event_id],["state","=", "done"]],
            views: [
                [false, 'list']
            ],
            target: "current"
        });
    }
}

EventDashboard.template = "custom_fsdc.EventDashboard";
registry.category("actions").add("event_dashboard_tag", EventDashboard)