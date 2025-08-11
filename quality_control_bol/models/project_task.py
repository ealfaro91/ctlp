
from odoo import api, fields, models


class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = ["project.task", "mail.thread", "mail.activity.mixin"]

    weight = fields.Integer(string="Weight", default=0, required=True, help="Weight of the task in percentage (0-100)")
    is_completed = fields.Boolean(string="Completed", default=False, help="Indicates if the task is completed")
    has_child = fields.Boolean(default=False, compute="_check_has_child")
    project_stage_id = fields.Many2one(
        "project.project.stage",
        string="Project Stage",
        tracking=True,
        help="The stage of the project this task belongs to.",
    )

    @api.depends('child_ids')
    def _check_has_child(self):
        for record in self:
            if len(record.child_ids) > 0:
                record.has_child = True
            else:
                record.has_child = False

    @api.onchange('weight')
    def _check_valid_weight(self):
        if self.weight < 0 or self.weight > 100:
            raise ValidationError("Weight value must be between 0 and 100")
        if not self.parent_id:
            cur_total = 0
            for task in self.project_id.task_ids:
                if task.id != self._origin.id and not task.parent_id:
                    cur_total += task.weight
            if (cur_total + self.weight) > 100:
                raise ValidationError("Total Weight from all task exceeded 100 (Exceed Amount:" + str(
                    cur_total + self.weight - 100) + ")")
        else:
            cur_total = 0
            for task in self.parent_id.child_ids:
                if task.id != self._origin.id:
                    cur_total += task.weight
            if (cur_total + self.weight) > 100:
                raise ValidationError("Total Weight from all task exceeded 100 (Exceed Amount:" + str(
                    cur_total + self.weight - 100) + ")")

        self._update_progress()

    @api.onchange('is_completed')
    def _task_completed_calc(self):
        if self.is_completed:
            self.development = 100
        else:
            self.development = 0
        self._update_progress()

    def _update_progress(self):
        record = self
        while record.parent_id:
            dev = 0
            for task in record.parent_id.child_ids:
                if task.id != self._origin.id:
                    dev += task.weight * task.development
                else:
                    dev += self.weight * self.development
            record.parent_id.development = dev / 100
            record = record.parent_id

        dev = 0
        for task in record.project_id.task_ids:
            if not task.parent_id:
                if task.id != self._origin.id:

                    dev += task.weight * task.development
                else:
                    dev += self.weight * self.development
        record.project_id.development = dev / 100
