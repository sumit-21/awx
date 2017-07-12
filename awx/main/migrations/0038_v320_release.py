# -*- coding: utf-8 -*-
# Python
from __future__ import unicode_literals

# Psycopg2
from psycopg2.extensions import AsIs

# Django
from django.db import migrations, models

# AWX
import awx.main.fields
from awx.main.models import Host


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_v313_instance_version'),
    ]

    operations = [
        # Release UJT unique_together constraint
        migrations.AlterUniqueTogether(
            name='unifiedjobtemplate',
            unique_together=set([]),
        ),

        # Inventory Refresh
        migrations.RenameField(
            'InventorySource',
            'group',
            'deprecated_group'
        ),
        migrations.AlterField(
            model_name='inventorysource',
            name='deprecated_group',
            field=models.OneToOneField(related_name='deprecated_inventory_source', null=True, default=None, to='main.Group'),
        ),
        migrations.AlterField(
            model_name='inventorysource',
            name='inventory',
            field=models.ForeignKey(related_name='inventory_sources', default=None, to='main.Inventory', null=True),
        ),

        # Smart Inventory
        migrations.AddField(
            model_name='inventory',
            name='host_filter',
            field=awx.main.fields.SmartFilterField(default=None, help_text='Filter that will be applied to the hosts of this inventory.', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='kind',
            field=models.CharField(default=b'', help_text='Kind of inventory being represented.', max_length=32, blank=True, choices=[(b'', 'Hosts have a direct link to this inventory.'), (b'smart', 'Hosts for inventory generated using the host_filter property.')]),
        ),
        migrations.CreateModel(
            name='SmartInventoryMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.ForeignKey(related_name='+', to='main.Host')),
            ],
        ),
        migrations.AddField(
            model_name='smartinventorymembership',
            name='inventory',
            field=models.ForeignKey(related_name='+', to='main.Inventory'),
        ),
        migrations.AddField(
            model_name='host',
            name='smart_inventories',
            field=models.ManyToManyField(related_name='_host_smart_inventories_+', through='main.SmartInventoryMembership', to='main.Inventory'),
        ),
        migrations.AlterUniqueTogether(
            name='smartinventorymembership',
            unique_together=set([('host', 'inventory')]),
        ),

        # Background Inventory deletion
        migrations.AddField(
            model_name='inventory',
            name='pending_deletion',
            field=models.BooleanField(default=False, help_text='Flag indicating the inventory is being deleted.', editable=False),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='organization',
            field=models.ForeignKey(related_name='inventories', on_delete=models.deletion.SET_NULL, to='main.Organization', help_text='Organization containing this inventory.', null=True),
        ),

        # Facts
        migrations.AlterField(
            model_name='fact',
            name='facts',
            field=awx.main.fields.JSONBField(default={}, help_text='Arbitrary JSON structure of module facts captured at timestamp for a single host.', blank=True),
        ),
        migrations.AddField(
            model_name='host',
            name='ansible_facts',
            field=awx.main.fields.JSONBField(default={}, help_text='Arbitrary JSON structure of most recent ansible_facts, per-host.', blank=True),
        ),
        migrations.AddField(
            model_name='host',
            name='ansible_facts_modified',
            field=models.DateTimeField(default=None, help_text='The date and time ansible_facts was last modified.', null=True, editable=False),
        ),
        migrations.AddField(
            model_name='job',
            name='use_fact_cache',
            field=models.BooleanField(default=False, help_text='If enabled, Tower will act as an Ansible Fact Cache Plugin; persisting facts at the end of a playbook run to the database and caching facts for use by Ansible.'),
        ),
        migrations.AddField(
            model_name='jobtemplate',
            name='use_fact_cache',
            field=models.BooleanField(default=False, help_text='If enabled, Tower will act as an Ansible Fact Cache Plugin; persisting facts at the end of a playbook run to the database and caching facts for use by Ansible.'),
        ),
        migrations.RunSQL([("CREATE INDEX host_ansible_facts_default_gin ON %s USING gin"
                            "(ansible_facts jsonb_path_ops);", [AsIs(Host._meta.db_table)])],
                          [('DROP INDEX host_ansible_facts_default_gin;', None)]),


        # SCM file-based inventories
        migrations.AddField(
            model_name='inventorysource',
            name='scm_last_revision',
            field=models.CharField(default=b'', max_length=1024, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='inventorysource',
            name='source_project',
            field=models.ForeignKey(related_name='scm_inventory_sources', default=None, blank=True, to='main.Project', help_text='Project containing inventory file used as source.', null=True),
        ),
        migrations.AddField(
            model_name='inventoryupdate',
            name='source_project_update',
            field=models.ForeignKey(related_name='scm_inventory_updates', default=None, blank=True, to='main.ProjectUpdate', help_text='Inventory files from this Project Update were used for the inventory update.', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='inventory_files',
            field=awx.main.fields.JSONField(default=[], help_text='Suggested list of content that could be Ansible inventory in the project', verbose_name='Inventory Files', editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='inventorysource',
            name='source',
            field=models.CharField(default=b'', max_length=32, blank=True, choices=[(b'', 'Manual'), (b'file', 'File, Directory or Script'), (b'scm', 'Sourced from a project in Tower'), (b'ec2', 'Amazon EC2'), (b'gce', 'Google Compute Engine'), (b'azure', 'Microsoft Azure Classic (deprecated)'), (b'azure_rm', 'Microsoft Azure Resource Manager'), (b'vmware', 'VMware vCenter'), (b'satellite6', 'Red Hat Satellite 6'), (b'cloudforms', 'Red Hat CloudForms'), (b'openstack', 'OpenStack'), (b'custom', 'Custom Script')]),
        ),
        migrations.AlterField(
            model_name='inventoryupdate',
            name='source',
            field=models.CharField(default=b'', max_length=32, blank=True, choices=[(b'', 'Manual'), (b'file', 'File, Directory or Script'), (b'scm', 'Sourced from a project in Tower'), (b'ec2', 'Amazon EC2'), (b'gce', 'Google Compute Engine'), (b'azure', 'Microsoft Azure Classic (deprecated)'), (b'azure_rm', 'Microsoft Azure Resource Manager'), (b'vmware', 'VMware vCenter'), (b'satellite6', 'Red Hat Satellite 6'), (b'cloudforms', 'Red Hat CloudForms'), (b'openstack', 'OpenStack'), (b'custom', 'Custom Script')]),
        ),
        migrations.AlterField(
            model_name='inventorysource',
            name='source_path',
            field=models.CharField(default=b'', max_length=1024, blank=True),
        ),
        migrations.AlterField(
            model_name='inventoryupdate',
            name='source_path',
            field=models.CharField(default=b'', max_length=1024, blank=True),
        ),
        migrations.AlterField(
            model_name='unifiedjob',
            name='launch_type',
            field=models.CharField(default=b'manual', max_length=20, editable=False, choices=[(b'manual', 'Manual'), (b'relaunch', 'Relaunch'), (b'callback', 'Callback'), (b'scheduled', 'Scheduled'), (b'dependency', 'Dependency'), (b'workflow', 'Workflow'), (b'sync', 'Sync'), (b'scm', 'SCM Update')]),
        ),
        migrations.AddField(
            model_name='inventorysource',
            name='update_on_project_update',
            field=models.BooleanField(default=False),
        ),

        # Named URL
        migrations.AlterField(
            model_name='notificationtemplate',
            name='name',
            field=models.CharField(max_length=512),
        ),
        migrations.AlterField(
            model_name='notificationtemplate',
            name='organization',
            field=models.ForeignKey(related_name='notification_templates', to='main.Organization', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='notificationtemplate',
            unique_together=set([('organization', 'name')]),
        ),

        # Add verbosity option to inventory updates
        migrations.AddField(
            model_name='inventorysource',
            name='verbosity',
            field=models.PositiveIntegerField(default=1, blank=True, choices=[(0, b'0 (WARNING)'), (1, b'1 (INFO)'), (2, b'2 (DEBUG)')]),
        ),
        migrations.AddField(
            model_name='inventoryupdate',
            name='verbosity',
            field=models.PositiveIntegerField(default=1, blank=True, choices=[(0, b'0 (WARNING)'), (1, b'1 (INFO)'), (2, b'2 (DEBUG)')]),
        ),

        # Job Templates
        migrations.AddField(
            model_name='jobtemplate',
            name='ask_verbosity_on_launch',
            field=models.BooleanField(default=False),
        ),

        # Workflows
        migrations.AddField(
            model_name='workflowjob',
            name='allow_simultaneous',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='workflowjobtemplate',
            name='allow_simultaneous',
            field=models.BooleanField(default=False),
        ),

        # Permission and Deprecated Field Removal
        migrations.RemoveField(
            model_name='permission',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='inventory',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='project',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='team',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='user',
        ),
        migrations.RemoveField(
            model_name='activitystream',
            name='permission',
        ),
        migrations.RemoveField(
            model_name='credential',
            name='deprecated_team',
        ),
        migrations.RemoveField(
            model_name='credential',
            name='deprecated_user',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='deprecated_admins',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='deprecated_projects',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='deprecated_users',
        ),
        migrations.RemoveField(
            model_name='team',
            name='deprecated_projects',
        ),
        migrations.RemoveField(
            model_name='team',
            name='deprecated_users',
        ),
        migrations.DeleteModel(
            name='Permission',
        ),

        # Insights
        migrations.AddField(
            model_name='host',
            name='insights_system_id',
            field=models.TextField(default=None, help_text='Red Hat Insights host unique identifier.', null=True, db_index=True, blank=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='insights_credential',
            field=models.ForeignKey(related_name='insights_inventories', on_delete=models.deletion.SET_NULL, default=None, blank=True, to='main.Credential', help_text='Credentials to be used by hosts belonging to this inventory when accessing Red Hat Insights API.', null=True),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='kind',
            field=models.CharField(default=b'', help_text='Kind of inventory being represented.', max_length=32, blank=True, choices=[(b'', 'Hosts have a direct link to this inventory.'), (b'smart', 'Hosts for inventory generated using the host_filter property.')]),
        ),

        # Timeout help text update
        migrations.AlterField(
            model_name='inventorysource',
            name='timeout',
            field=models.IntegerField(default=0, help_text='The amount of time (in seconds) to run before the task is canceled.', blank=True),
        ),
        migrations.AlterField(
            model_name='inventoryupdate',
            name='timeout',
            field=models.IntegerField(default=0, help_text='The amount of time (in seconds) to run before the task is canceled.', blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='timeout',
            field=models.IntegerField(default=0, help_text='The amount of time (in seconds) to run before the task is canceled.', blank=True),
        ),
        migrations.AlterField(
            model_name='jobtemplate',
            name='timeout',
            field=models.IntegerField(default=0, help_text='The amount of time (in seconds) to run before the task is canceled.', blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='timeout',
            field=models.IntegerField(default=0, help_text='The amount of time (in seconds) to run before the task is canceled.', blank=True),
        ),
        migrations.AlterField(
            model_name='projectupdate',
            name='timeout',
            field=models.IntegerField(default=0, help_text='The amount of time (in seconds) to run before the task is canceled.', blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='diff_mode',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='jobtemplate',
            name='diff_mode',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='adhoccommand',
            name='diff_mode',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='jobtemplate',
            name='ask_diff_mode_on_launch',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='job',
            name='diff_mode',
            field=models.BooleanField(default=False, help_text='If enabled, textual changes made to any templated files on the host are shown in the standard output'),
        ),
        migrations.AlterField(
            model_name='jobtemplate',
            name='diff_mode',
            field=models.BooleanField(default=False, help_text='If enabled, textual changes made to any templated files on the host are shown in the standard output'),
        ),
    ]
