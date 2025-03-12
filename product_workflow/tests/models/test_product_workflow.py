import sys

import pytest
from django.core.exceptions import ValidationError

from product_workflow.models import ProductWorkflow
from product_workflow.tests.constants import PYTHON_VERSION, PYTHON_VERSION_REASON

pytestmark = [
    pytest.mark.models,
    pytest.mark.skipif(sys.version_info < PYTHON_VERSION, reason=PYTHON_VERSION_REASON),
]


@pytest.mark.django_db
class TestProductWorkflow:
    """
    Tests for the ProductWorkflow model.

    This test class verifies the general functionality of the ProductWorkflow model,
    including its string representation and validation logic in the clean method.

    Tests:
    -------
    - test_str_representation: Verifies the __str__ method returns the expected format.
    - test_str_with_no_current_step: Ensures __str__ works when current_step is None.
    - test_clean_valid_instance: Tests that clean passes with a valid instance.
    - test_clean_duplicate_product_workflow: Tests that clean raises ValidationError for duplicates.
    - test_unique_constraint: Verifies the database-level unique constraint.
    """

    def test_str_with_no_first_step(self, product, workflow):
        """
        Test the __str__ method when no first step is assigned.

        Verifies that the string representation defaults to "None" for first_step.

        Args:
        ----
            product: Fixture providing a Product instance.
            workflow: Fixture providing a Workflow instance.

        Asserts:
        --------
            The __str__ output includes "None" for first_step.
        """
        product_workflow = ProductWorkflow.objects.create(
            product=product, workflow=workflow, first_step=None
        )
        expected_str = f"Product ID:{product.id} - Workflow ID:{workflow.id} (First Step: None)"
        assert str(product_workflow) == expected_str

    def test_clean_valid_instance(self, product, workflow):
        """
        Test that the clean method passes for a valid ProductWorkflow instance.

        Creates a new ProductWorkflow and ensures no ValidationError is raised.

        Args:
        ----
            product: Fixture providing a Product instance.
            workflow: Fixture providing a Workflow instance.
            step: Fixture providing a Step instance.
        """
        product_workflow = ProductWorkflow(
            product=product, workflow=workflow
        )
        try:
            product_workflow.clean()
        except ValidationError:
            pytest.fail("clean() raised ValidationError unexpectedly")

    def test_clean_duplicate_product_workflow(
        self, product_workflow, product, workflow, step
    ):
        """
        Test that the clean method raises ValidationError for a duplicate ProductWorkflow.

        Attempts to create a second ProductWorkflow with the same product and workflow,
        verifying that clean enforces the uniqueness constraint.

        Args:
        ----
            product_workflow: Fixture providing an existing ProductWorkflow instance.
            product: Fixture providing a Product instance.
            workflow: Fixture providing a Workflow instance.
            step: Fixture providing a Step instance.

        Asserts:
        --------
            A ValidationError is raised with the expected message.
        """
        duplicate_product_workflow = ProductWorkflow(
            product=product, workflow=workflow
        )
        with pytest.raises(ValidationError) as exc_info:
            duplicate_product_workflow.clean()
        assert "A product can only be associated with a workflow once" in str(
            exc_info.value
        )

    def test_unique_constraint(
        self, product_workflow, product, workflow, step
    ):
        """
        Test the database-level unique constraint on (product, workflow).

        Attempts to create a duplicate ProductWorkflow in the database and verifies
        that an IntegrityError (wrapped as a database exception) is raised.

        Args:
        ----
            product_workflow: Fixture providing an existing ProductWorkflow instance.
            product: Fixture providing a Product instance.
            workflow: Fixture providing a Workflow instance.
            step: Fixture providing a Step instance.

        Asserts:
        --------
            Creating a duplicate raises an exception (typically IntegrityError).
        """
        with pytest.raises(Exception) as exc_info:  # IntegrityError or similar
            ProductWorkflow.objects.create(
                product=product,
                workflow=workflow,
            )
        assert (
            "UNIQUE constraint failed:" in str(exc_info.value)
            or "duplicate" in str(exc_info.value).lower()
        )
